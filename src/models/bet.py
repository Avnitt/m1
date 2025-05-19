from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Bet(SQLModel, table=True):
    __tablename__ = "bets"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(foreign_key="users.username")
    market_id: str
    odds: float
    stake: float
    selection: str
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FancyBet(Bet):
    pass

class ExchangeBet(Bet):
    exchange_type: str
    status: str
    matched_amount: str