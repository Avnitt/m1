from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from ..models.bet import Bet

class MatchOrder(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    back_bet_id: int = Field(foreign_key="bets.id")
    lay_bet_id: int = Field(foreign_key="bets.id")
    matched_amount: float
    odds: float
    market_id: str
    runner: str
    created_at: datetime = Field(default_factory=datetime.utcnow)