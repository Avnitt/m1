# betting_engine.py
from sqlmodel import Session, select
from datetime import datetime
from ..models.bet import Bet
from ..models.match_order import MatchOrder
from ..models.user import User
from typing import Optional

class BettingEngine:
    def __init__(self, session: Session):
        self.session = session

    def place_bet(self, username: str, market_id: str, runner_name: str, odds: float, amount: float, bet_type: str) -> Bet:
        user = self.session.get(User, username)
        if user is None or user.balance < amount:
            raise ValueError("Insufficient balance")

        # Deduct funds
        user.balance -= amount
        self.session.add(user)

        new_bet = Bet(
            username=user.username,
            market_id=market_id,
            runner_name=runner_name,
            odds=odds,
            amount=amount,
            matched_amount=0.0,
            bet_type=bet_type,
            status="unmatched"
        )
        self.session.add(new_bet)
        self.session.commit()
        self.match_bets(new_bet)
        return new_bet

    def match_bets(self, new_bet: Bet):
        # Look for opposing bets
        opposing_type = "lay" if new_bet.bet_type == "back" else "back"
        possible_matches = self.session.exec(
            select(Bet).where(
                Bet.market_id == new_bet.market_id,
                Bet.runner_name == new_bet.runner_name,
                Bet.bet_type == opposing_type,
                Bet.status.in_(["unmatched", "partial"]),
                (Bet.odds >= new_bet.odds if new_bet.bet_type == "back" else Bet.odds <= new_bet.odds)
            ).order_by(Bet.odds.desc() if new_bet.bet_type == "back" else Bet.odds.asc())
        ).all()

        for match in possible_matches:
            available_to_match = match.amount - match.matched_amount
            required = new_bet.amount - new_bet.matched_amount

            if required <= 0:
                break

            matched_amt = min(required, available_to_match)
            match.matched_amount += matched_amt
            new_bet.matched_amount += matched_amt

            if match.matched_amount == match.amount:
                match.status = "matched"
            else:
                match.status = "partial"

            if new_bet.matched_amount == new_bet.amount:
                new_bet.status = "matched"
            else:
                new_bet.status = "partial"

            match_order = MatchOrder(
                market_id=new_bet.market_id,
                runner_name=new_bet.runner_name,
                back_bet_id=new_bet.id if new_bet.bet_type == "back" else match.id,
                lay_bet_id=new_bet.id if new_bet.bet_type == "lay" else match.id,
                odds=new_bet.odds,
                amount=matched_amt
            )
            self.session.add(match_order)
            self.session.add(match)
            self.session.add(new_bet)

        self.session.commit()

    def settle_market(self, market_id: str, winner: str):
        matched_orders = self.session.exec(select(MatchOrder).where(MatchOrder.market_id == market_id)).all()
        for order in matched_orders:
            back_bet = self.session.get(Bet, order.back_bet_id)
            lay_bet = self.session.get(Bet, order.lay_bet_id)

            # Determine outcome
            if order.runner_name == winner:
                # Backer wins
                self.credit_winnings(back_bet.user_id, order.amount * (order.odds - 1))
            else:
                # Layer wins (gets backer's amount)
                self.credit_winnings(lay_bet.user_id, order.amount)

            # Mark bets as settled
            back_bet.status = "settled"
            lay_bet.status = "settled"
            self.session.add(back_bet)
            self.session.add(lay_bet)

        self.session.commit()

    def credit_winnings(self, username: str, amount: float):
        user = self.session.get(User, username)
        user.balance += amount
        self.session.add(user)
        self.session.commit()

    def cash_out(self, username: str, bet_id: int, cash_out_odds: float) -> Optional[float]:
        bet = self.session.get(Bet, bet_id)
        if bet is None or bet.username != username or bet.status != "matched":
            return None

        potential_profit = bet.amount * (bet.odds - 1)
        cashed_amount = potential_profit * (cash_out_odds / bet.odds)

        user = self.session.get(User, username)
        user.balance += cashed_amount
        bet.status = "cashed_out"

        self.session.add(user)
        self.session.add(bet)
        self.session.commit()
        return cashed_amount
