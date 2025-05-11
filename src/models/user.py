from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(default=None, primary_key=True, index=True)
    username: str = Field(index=True, nullable=False)
    password: str = Field(nullable=False)
    balance: float
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, is_admin={self.is_admin}, is_active={self.is_active})"

    def __str__(self):
        return f"User: {self.username}, Admin: {self.is_admin}, Active: {self.is_active}"