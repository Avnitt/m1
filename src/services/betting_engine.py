from datetime import datetime
from sqlmodel import select
from ..database import SessionDep
from ..models.user import User
from ..models.bet import Bet, Event, Market, Runner
from ..schemas.bet import BetCreate
from ..services.redis_client import RedisClient
from fastapi import HTTPException

import logging, json

logging.basicConfig(level=logging.INFO)

async def ensure_event(db: SessionDep, redis_client: RedisClient, event_id: str):
    stmt = select(Event).where(Event.event_id == event_id)
    result = db.exec(stmt).first()

    if result:
        return
    
    data = await redis_client.get("events")
    events = json.loads(data)

    for event in events:
        if event["event_id"] == event_id:
            start_time = datetime.fromisoformat(event["openDate"].replace("Z", "+00:00"))
            new_event = Event(
                event_id=event_id,
                event_name=event["event_name"],
                start_time=start_time
                )
            db.add(new_event)
            db.commit()
            db.refresh(new_event)
        

async def ensure_market(db: SessionDep, redis_client: RedisClient, event_id: str, market_id: str):
    stmt = select(Market).where(Market.market_id == market_id)
    result = db.exec(stmt).first()

    if result:
        return
    
    data = await redis_client.get(f"markets:{event_id}")
    markets = json.loads(data)
    for category in ['bookMaker', 'fancy']:
        for m in markets.get(category, []):
            if m.get("marketId") == market_id:
                runners = m.get("runners", [])
                if runners:
                    for runner in runners:
                        new_runner = Runner(market_id=market_id, selection_name=runner.selectionName)
                        db.add(new_runner)
                        db.commit()

                else:
                    for runner in ["Yes", "No"]:
                        new_runner = Runner(market_id=market_id, selection_name=runner)
                        db.add(new_runner)
                        db.commit()

                new_market = Market(
                    event_id=event_id,
                    market_id=m["marketId"],
                    market_name=m["marketName"],
                    status=m["statusName"],
                    runners=runners
                )
                db.add(new_market)
                db.commit()
                return new_market


def place_bet_logic(db: SessionDep, username: str, bet_data: BetCreate) -> Bet:
    user = db.get(User, username)
    if not user or user.balance < bet_data.stake:
        raise HTTPException(status_code=400, detail="Insufficient balance or invalid user.")

    user.balance -= bet_data.stake
    bet = Bet(username=username, **bet_data.model_dump())
    db.add(bet)
    db.commit()
    db.refresh(bet)
    return bet


def settle_bets_logic(db: SessionDep, market_id: str, winning_selection: str):
    stmt = select(Bet).where(Bet.market_id == market_id).where(Bet.status == 'OPEN')
    bets = db.exec(stmt)
    for bet in bets:
        if bet.selection_name == winning_selection:
            win_amount = bet.stake * bet.odds
            user = db.query(User).filter(User.id == bet.user_id).first()
            user.balance += win_amount
            bet.is_won = True
        else:
            bet.is_won = False

        bet.is_settled = True

    db.commit()


def process_cashout_logic(db: SessionDep, bet_id: int, cashout_odds: float):
    bet = db.query(Bet).filter(Bet.id == bet_id).first()
    if not bet or bet.is_settled or bet.is_cashed_out:
        raise HTTPException(status_code=400, detail="Invalid or already settled bet.")

    cashout_amount = bet.stake * cashout_odds
    user = db.query(User).filter(User.id == bet.user_id).first()
    user.balance += cashout_amount

    bet.is_cashed_out = True
    bet.cashed_out_amount = cashout_amount
    bet.is_settled = True
    bet.is_won = None

    db.commit()
    return cashout_amount