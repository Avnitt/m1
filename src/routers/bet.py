# endpoints/betting.py
from fastapi import APIRouter, Depends, Request
from sqlmodel import select
from ..models.bet import Bet
from ..models.user import User
from ..schemas.bet import BetCreate, BetHistory, BetResponse, BetSettle
from ..schemas.user import UserOut
from ..dependencies import get_current_user
from ..database import SessionDep
from ..services.betting_engine import place_bet_logic, settle_bets_logic, process_cashout_logic, ensure_event, ensure_market

router = APIRouter(prefix="/betting", tags=["betting"])

@router.post("/place_bet/{event_id}", response_model=BetResponse)
async def place_bet(
    event_id: str,
    payload: BetCreate,
    request: Request,
    db: SessionDep,
    user: User = Depends(get_current_user)
):
    redis_client = request.app.state.redis_client
    await ensure_event(db, redis_client, event_id)
    await ensure_market(db, redis_client, event_id, payload.market_id)
    return place_bet_logic(db, user.username, payload)


@router.post("/settle_bet")
async def settle_bet(
    payload: BetSettle,
    db: SessionDep
):
    return settle_bets_logic(payload, db)


# @router.post("/cashout")
# async def cashout(
#     payload: CashoutRequest,
#     db: SessionDep,
#     user: User = Depends(get_current_user)
# ):
#     return await process_cashout(user, payload, db)


@router.get("/history", response_model=list[BetHistory])
async def get_bet_history(
    db: SessionDep,
    user: User = Depends(get_current_user)
):
    result = db.exec(select(Bet).where(Bet.username == user.username).order_by(Bet.placed_at.desc())).all()
    return [BetHistory.model_validate(b.model_dump()) for b in result]


@router.get("/balance", response_model=UserOut)
async def get_user_balance(
    user: User = Depends(get_current_user)
):
    return UserOut(
        username=user.username,
        balance=user.balance,
        )
