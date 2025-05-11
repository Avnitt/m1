from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    balance: float

class UserCreate(UserBase):
    is_admin: bool = False
    password: str

class UserOut(UserBase):
    class Config:
        from_attributes = True