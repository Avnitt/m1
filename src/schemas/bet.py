from datetime import datetime
from typing import Optional
from pydantic import BaseModel


#     username: str = Field(foreign_key="user.username")
#     market_id: str
#     odds: float
#     stake: float
#     selection: str
    
#     created_at: datetime = Field(default_factory=datetime.utcnow)

# class FancyBet(Bet):
#     pass

# class ExchangeBet(Bet):
#     exchange_type: str
#     status: str
#     matched_amount: str


class PlaceFancyBet(BaseModel):
    market_id: str
    odds: float
    stake: float
    selection: str

class PlaceExchangeBet(PlaceFancyBet):
    exchange_type:str

class PlaceBetResponse(PlaceFancyBet):
    exchange_type: Optional[str]
    created_at: datetime
    
class SettleBetRequest(BaseModel):
    pass

class CashoutRequest(BaseModel):
    pass
    
class BetHistoryResponse(BaseModel):
    market_name: str
    odds: float
    stake: float
    selection: float
    exchange_type: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class UserBalanceResponse(BaseModel):
    username: str
    balance: float