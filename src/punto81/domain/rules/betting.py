"""Betting actions and legality rules for a 5-card draw round."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from punto81.domain.models.money import (
    ZERO_CHIPS,
    Bankroll,
    Chips,
    InsufficientFundsError,
    Pot,
    chips,
)


class BetActionKind(Enum):
    """Distinct kinds of action a player can take during a betting round."""

    CHECK = "check"
    BET = "bet"
    CALL = "call"
    RAISE = "raise"
    FOLD = "fold"


class IllegalActionError(ValueError):
    """The requested action is not legal in the current state."""


@dataclass(frozen=True, slots=True)
class BetAction:
    """A concrete action taken during a betting round.

    Attributes:
        kind: the kind of action.
        amount: the chips moved out of the player's bankroll by this
            action (call amount, raise amount, opening bet). ``0`` for
            check and fold.
    """

    kind: BetActionKind
    amount: Chips = ZERO_CHIPS


@dataclass(frozen=True, slots=True)
class RoundState:
    """Snapshot of the betting round after applying actions.

    Attributes:
        human: human bankroll.
        cpu: CPU bankroll.
        pot: chips currently in the pot.
        current_bet: amount the next player must match to stay in.
        human_committed: chips the human has already pushed this round.
        cpu_committed: chips the CPU has already pushed this round.
        folded: whichever player has folded, or ``None``.
    """

    human: Bankroll
    cpu: Bankroll
    pot: Pot
    current_bet: Chips = ZERO_CHIPS
    human_committed: Chips = ZERO_CHIPS
    cpu_committed: Chips = ZERO_CHIPS
    folded: str | None = None


@dataclass(frozen=True, slots=True)
class _BetMove:
    """Internal computed effect of an action."""

    debit: Chips
    new_current_bet: Chips


def _compute_move(action: BetAction, state: RoundState, committed: Chips) -> _BetMove:
    """Translate a logical action into chips to debit and new current bet."""
    match action.kind:
        case BetActionKind.CHECK:
            if state.current_bet != committed:
                raise IllegalActionError("cannot check when facing a bet")
            return _BetMove(debit=chips(0), new_current_bet=state.current_bet)

        case BetActionKind.FOLD:
            return _BetMove(debit=chips(0), new_current_bet=state.current_bet)

        case BetActionKind.BET:
            if state.current_bet != committed:
                raise IllegalActionError("use raise instead of bet when facing one")
            if action.amount <= 0:
                raise IllegalActionError("bet amount must be positive")
            return _BetMove(debit=action.amount, new_current_bet=action.amount)

        case BetActionKind.CALL:
            to_call = chips(state.current_bet - committed)
            return _BetMove(debit=to_call, new_current_bet=state.current_bet)

        case BetActionKind.RAISE:
            if action.amount <= 0:
                raise IllegalActionError("raise amount must be positive")
            raise_to_call = int(state.current_bet) - int(committed)
            return _BetMove(
                debit=chips(raise_to_call + int(action.amount)),
                new_current_bet=chips(int(state.current_bet) + int(action.amount)),
            )


def apply_action(state: RoundState, actor: str, action: BetAction) -> RoundState:
    """Apply a player's action and return the new ``RoundState``.

    Args:
        state: the current round state.
        actor: either ``"human"`` or ``"cpu"``.
        action: the action to apply.

    Returns:
        A new ``RoundState`` reflecting the action.

    Raises:
        IllegalActionError: if the action violates the rules.
        InsufficientFundsError: if the player cannot afford the debit.
    """
    if state.folded is not None:
        raise IllegalActionError("the round is already over")
    if actor not in {"human", "cpu"}:
        raise IllegalActionError(f"unknown actor: {actor}")

    committed = state.human_committed if actor == "human" else state.cpu_committed
    move = _compute_move(action, state, committed)

    bankroll = state.human if actor == "human" else state.cpu
    if not bankroll.can_afford(move.debit):
        raise InsufficientFundsError(f"{actor} cannot afford to move {move.debit} chips")

    new_bankroll = bankroll.debit(move.debit)
    new_pot = state.pot.add(move.debit)
    new_committed = chips(committed + move.debit)

    if action.kind is BetActionKind.FOLD:
        return _with_fold(state, actor)

    if actor == "human":
        return RoundState(
            human=new_bankroll,
            cpu=state.cpu,
            pot=new_pot,
            current_bet=move.new_current_bet,
            human_committed=new_committed,
            cpu_committed=state.cpu_committed,
            folded=None,
        )
    return RoundState(
        human=state.human,
        cpu=new_bankroll,
        pot=new_pot,
        current_bet=move.new_current_bet,
        human_committed=state.human_committed,
        cpu_committed=new_committed,
        folded=None,
    )


def _with_fold(state: RoundState, actor: str) -> RoundState:
    return RoundState(
        human=state.human,
        cpu=state.cpu,
        pot=state.pot,
        current_bet=state.current_bet,
        human_committed=state.human_committed,
        cpu_committed=state.cpu_committed,
        folded=actor,
    )


def is_round_closed(state: RoundState, history: tuple[BetAction, ...]) -> bool:
    """Whether the round is over (fold or both matched after a chance to act).

    Args:
        state: current round state.
        history: actions in order. The round closes when somebody has
            folded or when both committed the same amount and the last
            actor was a check/call (not an opening bet/raise).
    """
    if state.folded is not None:
        return True
    if state.human_committed != state.cpu_committed:
        return False
    if not history:
        return False
    last_kind = history[-1].kind
    return last_kind in {BetActionKind.CHECK, BetActionKind.CALL}
