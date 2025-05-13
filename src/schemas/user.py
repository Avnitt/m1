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

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str

class RefreshRequest(BaseModel):
    refresh_token: str

class BalanceRequest(BaseModel):
    balance: float
    type: str

class PasswordChangeRequest(BaseModel):
    password: str