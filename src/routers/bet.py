# endpoints/betting.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from models import User, Bet, MatchOrder
from schemas import (
    PlaceBetRequest, PlaceBetResponse, 
    SettleBetRequest, CashoutRequest, 
    BetHistoryResponse, UserBalanceResponse
)
from dependencies import get_current_user, get_db_session
from services.betting_engine import place_bet_logic, settle_bet_logic, process_cashout_logic

router = APIRouter(prefix="/betting", tags=["Betting"])

@router.post("/place_bet", response_model=PlaceBetResponse)
async def place_bet(
    payload: PlaceBetRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    return await place_bet_logic(user, payload, db)


@router.post("/settle_bet")
async def settle_bet(
    payload: SettleBetRequest,
    db: AsyncSession = Depends(get_db_session)
):
    return await settle_bet_logic(payload, db)


@router.post("/cashout")
async def cashout(
    payload: CashoutRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    return await process_cashout_logic(user, payload, db)


@router.get("/history", response_model=list[BetHistoryResponse])
async def get_bet_history(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    result = await db.execute(select(Bet).where(Bet.user_id == user.id).order_by(Bet.timestamp.desc()))
    bets = result.scalars().all()
    return [BetHistoryResponse.from_orm(b) for b in bets]


@router.get("/balance", response_model=UserBalanceResponse)
async def get_user_balance(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_session)
):
    return UserBalanceResponse(balance=user.balance)
