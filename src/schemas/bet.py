from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from src.models.bet import Bet

class BetCreate(BaseModel):
    market_id: str
    market_name: str
    selection: str
    odds: float
    stake: float

class BetResponse(BaseModel):
    id: int
    username: str
    market_id: str
    selection: str
    odds: float
    stake: float
    status: str
    placed_at: datetime

    class Config:
        from_attributes = True

class BetHistory(BaseModel):
    market_name: str
    selection: str
    odds: float
    stake: float
    status: str
    placed_at: datetime
    settled_at: Optional[datetime] = None

class BetSettle(BaseModel):
    market_id: str
    selection: str

class EventResponse(BaseModel):
    event_id: str
    event_name: str
    start_time: datetime

    class Config:
        from_attributes = True

class MarketResponse(BaseModel):
    market_id: str
    market_name: str
    status: str
    bets: Optional[List[BetHistory]] = None

    class Config:
        from_attributes = True