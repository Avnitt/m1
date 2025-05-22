from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from jose import ExpiredSignatureError, JWTError, jwt
from datetime import datetime
import os

from ..database import SessionDep
from ..dependencies import create_access_token, create_refresh_token, authenticate_user, get_current_admin, get_current_user
from ..utils.hashing import get_password_hash
from ..models.user import User
from ..schemas.user import LoginRequest, RefreshRequest, Token, UserOut, PasswordChangeRequest

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/token", response_model=Token)
async def login(
    payload: LoginRequest,
    db: SessionDep
):
    try:
        user = await authenticate_user(db, payload.username, payload.password)
    except HTTPException as e:
        raise e
    
    access_token = create_access_token(user.username)
    refresh_token = create_refresh_token(user.username)
    
    user.refresh_token = refresh_token
    db.commit()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.post("/refresh", response_model=Token)
async def refresh_tokens(
    request: RefreshRequest,
    db: SessionDep
):
    try:
        payload = jwt.decode(
            request.refresh_token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        username = payload.get("sub")
    except (JWTError, ExpiredSignatureError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    # Get user from database
    user = db.get(User, username)
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
    new_access_token = create_access_token(user.username)
    new_refresh_token = create_refresh_token(user.username)

    # Update refresh token in database
    user.refresh_token = new_refresh_token
    db.commit()
    db.refresh(user)
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@router.post("/password_reset", response_model=UserOut)
async def change_password(db: SessionDep, user: Annotated[User, Depends(get_current_user)], request: PasswordChangeRequest):
    db_user = db.get(User, user.username)
    db_user.password = get_password_hash(request.password)
    db.add(user)
    db.commit()
    return user

@router.get("/test_user")
async def test_user(user: Annotated[User, Depends(get_current_user)]):
    return {"msg": "user"}

@router.get("/test_admin")
async def test_admin(user: Annotated[User, Depends(get_current_admin)]):
    return {"msg": "admin"}