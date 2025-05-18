from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Bet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(foreign_key="user.username")
    market_id: str
    runner: str
    odds: float
    amount: float
    bet_type: str  # "back" or "lay"
    status: str = "unmatched"  # "matched", "unmatched", "settled"
    matched_amount: float = 0.0
    potential_profit: float = 0.0
    potential_liability: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

