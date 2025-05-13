from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from typing import Annotated
import os

from .database import SessionDep
from .models.user import User
from .utils.hashing import verify_password

from dotenv import load_dotenv

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def authenticate_user(db: SessionDep, username: str, password: str) -> User:
    user = db.get(User, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    if not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    return user

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
            JWT_SECRET_KEY, 
            algorithms=[JWT_ALGORITHM]
        )
        username = payload.get("sub")
    except ExpiredSignatureError:
        raise expired_exception
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = db.get(User, username)
    if user is None or user.refresh_token is None:
        raise credentials_exception
        
    return user

async def get_current_admin(
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
    admin_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User is not admin",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET_KEY, 
            algorithms=[JWT_ALGORITHM]
        )
        username = payload.get("sub")
    except ExpiredSignatureError:
        raise expired_exception
    except (JWTError, ValueError):
        raise credentials_exception
    
    user = db.get(User, username)
    if user is None or user.refresh_token is None:
        raise credentials_exception
    
    if not user.is_admin:
        raise admin_exception
        
    return user

def create_access_token(username: str):
    expires = timedelta(minutes=float(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15)))
    return jwt.encode(
        {
            "sub": username,
            "exp": datetime.utcnow() + expires,
            "type": "access"
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

def create_refresh_token(username: str):
    expires = timedelta(days=float(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7)))
    return jwt.encode(
        {
            "sub": username,
            "exp": datetime.utcnow() + expires,
            "type": "refresh"
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM
    )

