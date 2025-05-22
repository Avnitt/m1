from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Relationship, SQLModel, Field
from datetime import datetime

if TYPE_CHECKING:
    from .user import User

class Event(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str
    event_name: str
    start_time: datetime

    markets: Optional[List["Market"]] = Relationship(back_populates="event")

class Market(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(foreign_key="event.event_id")
    market_id: str = Field(index=True)
    market_name: str
    status: str

    event: Optional["Event"] = Relationship(back_populates="markets")
    bets: Optional[List["Bet"]] = Relationship(back_populates="market")
    runners: Optional[List["Runner"]] = Relationship(back_populates="market")

class Runner(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    selection_name: str
    market_id: str = Field(foreign_key="market.market_id")

    market: Optional["Market"] = Relationship(back_populates="runners")

class Bet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(foreign_key="user.username")
    market_id: str = Field(foreign_key="market.market_id")
    market_name: str
    selection: str
    stake: float
    odds: float
    payout: float = Field(default=0)
    status: str = "OPEN"
    placed_at: datetime = Field(default_factory=datetime.now)
    settled_at: datetime = Field(default=None, nullable=True)
    
    user: Optional["User"] = Relationship(back_populates="bets")
    market: Optional["Market"] = Relationship(back_populates="bets")