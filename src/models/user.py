from typing import Optional
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    username: str = Field(primary_key=True, index=True)
    password: str = Field(nullable=False)
    balance: float
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    refresh_token: Optional[str] = Field(default=None, nullable=True)

    def __repr__(self):
        return f"User(username={self.username}, is_admin={self.is_admin}, is_active={self.is_active})"

    def __str__(self):
        return f"User: {self.username}, Admin: {self.is_admin}, Active: {self.is_active}"