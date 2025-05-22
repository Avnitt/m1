from typing import TYPE_CHECKING, Optional, List
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .bet import Bet


class User(SQLModel, table=True):
    username: str = Field(primary_key=True, index=True)
    password: str = Field(nullable=False)
    balance: float
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    refresh_token: Optional[str] = Field(default=None, nullable=True)

    bets: Optional[List["Bet"]] = Relationship(back_populates="user")

    def __repr__(self):
        return f"User(username={self.username}, is_admin={self.is_admin}, is_active={self.is_active})"

    def __str__(self):
        return f"User: {self.username}, Admin: {self.is_admin}, Active: {self.is_active}"
    

class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(foreign_key="user.username")
    amount: int
    type: str
    final_balance: str

    created_at: str