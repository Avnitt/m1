from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from fastapi.security import OAuth2AuthorizationCodeBearer
from jose import ExpiredSignatureError, JWTError, jwt
from datetime import datetime
import os

from sqlmodel import select

from ..database import SessionDep
from ..dependencies import create_access_token, create_refresh_token
from ..models.user import User
from ..schemas.user import RefreshRequest, LoginRequest, Token

from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/token")
async def login(request: LoginRequest, db: SessionDep, response_model=Token):
    try:
        user = db.get(User, request.username)

    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    try:
        user.verify_password_hash(request.password)

    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)
    
    user.refresh_token = refresh_token
    await db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.post("/refresh")
async def refresh_tokens(
    request: RefreshRequest,
    db: SessionDep
):
    try:
        payload = jwt.decode(
            request.refresh_token,
            os.getenv("JWT_SECRET_KEY"),
            algorithms=[os.getenv("JWT_ALGORITHM")]
        )
        user_id = int(payload.get("sub"))
    except (JWTError, ExpiredSignatureError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Get user from database
    user = await db.get(User, user_id)
    if not user or user.refresh_token != request.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Check refresh token expiration
    if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )

    # Generate new tokens
    new_access_token = create_access_token(user.id)
    new_refresh_token = create_refresh_token(user.id)

    # Update refresh token in database
    user.refresh_token = new_refresh_token
    await db.commit()
    await db.refresh(user)

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }