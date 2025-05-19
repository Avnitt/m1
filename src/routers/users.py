from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select
from ..models.user import User
from ..schemas.user import UserCreate, UserOut, BalanceRequest
from ..database import SessionDep
from ..dependencies import get_current_admin
from ..utils.hashing import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(get_current_admin)]
)

@router.get("/", response_model=list[UserOut])
async def get_users(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100) -> list[UserOut]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@router.get("/{username}", response_model=UserOut)
async def get_user(username: str, session: SessionDep) -> UserOut:
    user = session.get(User, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=UserOut)
async def create_user(user: UserCreate, session: SessionDep) -> UserOut:
    db_user = session.get(User, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = User.model_validate(user)
    user.password = get_password_hash(user.password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.patch("/{username}", response_model=UserOut)
async def add_or_deduct_balance(username: str, request: BalanceRequest, session: SessionDep) -> UserOut:
    db_user = session.get(User, username)
    curr_balance = db_user.balance
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if request.type == "deposit":
        curr_balance += request.balance

    if request.type == "withdrawl" and request.balance <= curr_balance:
        curr_balance = request.balance
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="can't withdraw more than current balance"
        )

    session.commit()
    session.refresh(db_user)
    return db_user

@router.delete("/{username}", response_model=UserOut)
def delete_user(username: str, session: SessionDep) -> UserOut:
    user = session.get(User, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return user