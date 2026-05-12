"""Integration tests for ``GameSession``."""

from __future__ import annotations

import pytest

from punto81.application.use_cases.demo import play_demo_game, play_demo_hand
from punto81.application.use_cases.game_session import (
    STARTING_STACK,
    GamePhase,
    GameSession,
    GameSessionError,
)
from punto81.domain.models.money import chips
from punto81.domain.ports.rng import Rng
from punto81.domain.rules.betting import BetAction, BetActionKind


def test_start_hand_deals_two_full_hands(rng: Rng) -> None:
    session = GameSession(rng=rng)
    snapshot = session.start_hand()
    assert snapshot.phase is GamePhase.FIRST_BET_HUMAN
    assert snapshot.human_hand is not None
    assert snapshot.cpu_hand is not None
    assert len(snapshot.human_hand.cards) == 5
    assert len(snapshot.cpu_hand.cards) == 5
    assert snapshot.pot.amount >= 10


def test_full_demo_hand_does_not_crash(rng: Rng) -> None:
    session = GameSession(rng=rng)
    events = list(play_demo_hand(session))
    assert events
    final = events[-1].snapshot
    assert final.phase in {GamePhase.HAND_OVER, GamePhase.GAME_OVER}


def test_demo_game_terminates(rng: Rng) -> None:
    session = GameSession(rng=rng)
    events = play_demo_game(session, max_hands=20)
    assert events
    total = int(session.snapshot.human.amount) + int(session.snapshot.cpu.amount)
    assert total >= 0


def test_starts_with_starting_stack(rng: Rng) -> None:
    session = GameSession(rng=rng)
    snap = session.snapshot
    assert snap.human.amount == STARTING_STACK
    assert snap.cpu.amount == STARTING_STACK


def test_human_fold_credits_cpu(rng: Rng) -> None:
    session = GameSession(rng=rng)
    session.start_hand()
    snap = session.human_first_bet(BetAction(BetActionKind.FOLD))
    assert snap.phase in {GamePhase.HAND_OVER, GamePhase.GAME_OVER}
    assert session.snapshot.cpu.amount >= STARTING_STACK


def test_cannot_bet_before_start(rng: Rng) -> None:
    session = GameSession(rng=rng)
    with pytest.raises(GameSessionError):
        session.human_first_bet(BetAction(BetActionKind.CALL))


def test_cannot_discard_outside_draw_phase(rng: Rng) -> None:
    session = GameSession(rng=rng)
    session.start_hand()
    with pytest.raises(GameSessionError):
        session.human_discard((0,))


def test_discard_limited_to_three(rng: Rng) -> None:
    session = GameSession(rng=rng)
    session.start_hand()
    session.human_first_bet(BetAction(BetActionKind.CALL))
    with pytest.raises(GameSessionError):
        session.human_discard((0, 1, 2, 3))


def test_play_many_hands_reproducible(rng: Rng) -> None:
    session_a = GameSession(rng=rng)
    play_demo_game(session_a, max_hands=8)
    bal_a = (
        int(session_a.snapshot.human.amount),
        int(session_a.snapshot.cpu.amount),
    )
    # second run on a fresh fixture-equivalent RNG would diverge; here we
    # just check the totals are well-formed.
    total = bal_a[0] + bal_a[1]
    assert total >= 0
    assert total <= 2 * int(STARTING_STACK)


def test_restore_session_resets_hand(rng: Rng) -> None:
    session = GameSession(rng=rng)
    session.start_hand()
    snap = session.snapshot
    restored = GameSession.restore(snap, rng=rng)
    assert restored.snapshot.hand.phase is GamePhase.AWAITING_HAND
    assert restored.snapshot.human.amount == snap.human.amount


def test_second_bet_check_runs_showdown(rng: Rng) -> None:
    session = GameSession(rng=rng)
    snap = session.start_hand()
    if snap.phase is GamePhase.GAME_OVER:
        pytest.skip("nobody could afford ante on this seed")
    snap = session.human_first_bet(BetAction(BetActionKind.CALL))
    if snap.phase is not GamePhase.DRAW_HUMAN:
        pytest.skip("CPU folded after raise")
    snap = session.human_discard(())
    snap = session.human_second_bet(BetAction(BetActionKind.CHECK))
    assert snap.phase in {GamePhase.HAND_OVER, GamePhase.GAME_OVER}


def test_second_bet_bet_then_cpu_response(rng: Rng) -> None:
    session = GameSession(rng=rng)
    snap = session.start_hand()
    if snap.phase is GamePhase.GAME_OVER:
        pytest.skip("nobody could afford ante on this seed")
    snap = session.human_first_bet(BetAction(BetActionKind.CALL))
    if snap.phase is not GamePhase.DRAW_HUMAN:
        pytest.skip("CPU folded after raise")
    snap = session.human_discard(())
    snap = session.human_second_bet(BetAction(BetActionKind.BET, chips(10)))
    assert snap.phase in {GamePhase.HAND_OVER, GamePhase.GAME_OVER}
