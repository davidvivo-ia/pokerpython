"""Tests for the betting rules."""

from __future__ import annotations

import pytest

from punto81.domain.models.money import (
    Bankroll,
    InsufficientFundsError,
    Pot,
    chips,
)
from punto81.domain.rules.betting import (
    BetAction,
    BetActionKind,
    IllegalActionError,
    RoundState,
    apply_action,
    is_round_closed,
)


def _initial_state() -> RoundState:
    return RoundState(
        human=Bankroll(chips(100)),
        cpu=Bankroll(chips(100)),
        pot=Pot(),
    )


def test_bet_then_call_closes_round() -> None:
    state = _initial_state()
    state = apply_action(state, "cpu", BetAction(BetActionKind.BET, chips(10)))
    state = apply_action(state, "human", BetAction(BetActionKind.CALL))
    history = (
        BetAction(BetActionKind.BET, chips(10)),
        BetAction(BetActionKind.CALL),
    )
    assert state.pot.amount == 20
    assert is_round_closed(state, history) is True


def test_check_check_closes_round() -> None:
    state = _initial_state()
    state = apply_action(state, "cpu", BetAction(BetActionKind.CHECK))
    state = apply_action(state, "human", BetAction(BetActionKind.CHECK))
    history = (BetAction(BetActionKind.CHECK), BetAction(BetActionKind.CHECK))
    assert is_round_closed(state, history) is True


def test_check_when_facing_bet_is_illegal() -> None:
    state = _initial_state()
    state = apply_action(state, "cpu", BetAction(BetActionKind.BET, chips(10)))
    with pytest.raises(IllegalActionError, match="cannot check"):
        apply_action(state, "human", BetAction(BetActionKind.CHECK))


def test_raise_increases_current_bet() -> None:
    state = _initial_state()
    state = apply_action(state, "cpu", BetAction(BetActionKind.BET, chips(10)))
    state = apply_action(state, "human", BetAction(BetActionKind.RAISE, chips(20)))
    assert state.current_bet == 30
    assert state.human_committed == 30
    assert state.cpu_committed == 10


def test_fold_marks_round_over() -> None:
    state = _initial_state()
    state = apply_action(state, "cpu", BetAction(BetActionKind.BET, chips(10)))
    state = apply_action(state, "human", BetAction(BetActionKind.FOLD))
    assert state.folded == "human"
    assert is_round_closed(state, (BetAction(BetActionKind.FOLD),)) is True


def test_insufficient_funds_raises() -> None:
    state = RoundState(
        human=Bankroll(chips(5)),
        cpu=Bankroll(chips(100)),
        pot=Pot(),
    )
    with pytest.raises(InsufficientFundsError):
        apply_action(state, "human", BetAction(BetActionKind.BET, chips(20)))


def test_unknown_actor_rejected() -> None:
    state = _initial_state()
    with pytest.raises(IllegalActionError, match="unknown actor"):
        apply_action(state, "bot", BetAction(BetActionKind.CHECK))


def test_bet_must_be_positive() -> None:
    state = _initial_state()
    with pytest.raises(IllegalActionError, match="positive"):
        apply_action(state, "cpu", BetAction(BetActionKind.BET, chips(0)))


def test_raise_must_be_positive() -> None:
    state = _initial_state()
    state = apply_action(state, "cpu", BetAction(BetActionKind.BET, chips(5)))
    with pytest.raises(IllegalActionError, match="positive"):
        apply_action(state, "human", BetAction(BetActionKind.RAISE, chips(0)))


def test_bet_when_facing_bet_is_illegal() -> None:
    state = _initial_state()
    state = apply_action(state, "cpu", BetAction(BetActionKind.BET, chips(5)))
    with pytest.raises(IllegalActionError, match="raise instead"):
        apply_action(state, "human", BetAction(BetActionKind.BET, chips(10)))


def test_actions_on_closed_round_rejected() -> None:
    state = _initial_state()
    state = apply_action(state, "human", BetAction(BetActionKind.FOLD))
    with pytest.raises(IllegalActionError, match="already over"):
        apply_action(state, "cpu", BetAction(BetActionKind.CHECK))


def test_empty_history_is_not_closed() -> None:
    state = _initial_state()
    assert is_round_closed(state, ()) is False
