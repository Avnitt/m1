from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from typing import Annotated
import os

from .database import SessionDep
from .models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: SessionDep
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    expired_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            os.getenv("JWT_SECRET_KEY"), 
            algorithms=[os.getenv("JWT_ALGORITHM")]
        )
        user_id: int = int(payload.get("sub"))
    except ExpiredSignatureError:
        raise expired_exception
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = await db.get(User, user_id)
    if user is None or user.refresh_token is None:
        raise credentials_exception
        
    return user

def create_access_token(user_id: int):
    expires = timedelta(minutes=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15)))
    return jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.utcnow() + expires,
            "type": "access"
        },
        os.getenv("JWT_SECRET_KEY"),
        algorithm=os.getenv("JWT_ALGORITHM")
    )

def create_refresh_token(user_id: int):
    expires = timedelta(days=float(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)))
    return jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.utcnow() + expires,
            "type": "refresh"
        },
        os.getenv("JWT_SECRET_KEY"),
        algorithm=os.getenv("JWT_ALGORITHM")
    )