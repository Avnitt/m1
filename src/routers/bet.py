# endpoints/betting.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from ..models.bet import Bet
from ..models.user import User
from ..models.match_order import MatchOrder
from ..schemas.bet import (
    PlaceFancyBet, PlaceExchangeBet,
    PlaceBetResponse, SettleBetRequest,
    CashoutRequest, BetHistoryResponse,
)
from ..schemas.user import UserOut
from ..dependencies import get_current_user
from ..database import SessionDep
from ..services.betting_engine import place_exchange_bet, place_fancy_bet, settle_bet_logic, process_cashout

router = APIRouter(prefix="/betting", tags=["Betting"])

@router.post("/place_fancy", response_model=PlaceBetResponse)
async def place_fancy(
    payload: PlaceFancyBet,
    db: SessionDep,
    user: User = Depends(get_current_user)
):
    return place_fancy_bet(user, payload, db)


@router.post("/place_exchange", response_model=PlaceBetResponse)
async def place_exchange(
    payload: PlaceExchangeBet,
    db: SessionDep,
    user: User = Depends(get_current_user)
):
    return place_exchange_bet(user, payload, db)


# @router.post("/settle_bet")
# async def settle_bet(
#     payload: SettleBetRequest,
#     db: SessionDep
# ):
#     return await settle_bet_logic(payload, db)


# @router.post("/cashout")
# async def cashout(
#     payload: CashoutRequest,
#     db: SessionDep,
#     user: User = Depends(get_current_user)
# ):
#     return await process_cashout(user, payload, db)


@router.get("/history", response_model=list[BetHistoryResponse])
async def get_bet_history(
    db: SessionDep,
    user: User = Depends(get_current_user)
):
    result = db.exec(select(Bet).where(Bet.username == user.username).order_by(Bet.timestamp.desc())).all()
    return [BetHistoryResponse.model_validate(b) for b in result]


@router.get("/balance", response_model=UserOut)
async def get_user_balance(
    user: User = Depends(get_current_user)
):
    return UserOut(
        username=user.username,
        balance=user.balance,
        )
