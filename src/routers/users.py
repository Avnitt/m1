from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlmodel import select
from ..models.user import User
from ..schemas.user import UserCreate, UserOut
from ..database import SessionDep

router = APIRouter(tags=["users"])

@router.get("/users", response_model=list[UserOut])
async def get_users(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100) -> list[UserOut]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int, session: SessionDep) -> UserOut:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/users", response_model=UserOut)
async def create_user(user: UserCreate, session: SessionDep) -> UserOut:
    db_user = session.get(User, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = User.model_validate(user)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.patch("/users/{user_id}", response_model=UserOut)
async def partial_update_user(user_id: int, user: User, session: SessionDep) -> UserOut:
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    for key, value in user.model_dump(exclude_unset=True).items():
        if value:
            setattr(db_user, key, value)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}", response_model=UserOut)
def delete_hero(user_id: int, session: SessionDep) -> UserOut:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return user