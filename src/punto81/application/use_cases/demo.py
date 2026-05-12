"""Deterministic demo driver.

Plays a self-contained game without any human interaction. Used by
``punto81 --demo`` and as an E2E smoke test.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from punto81.application.use_cases.game_session import (
    GamePhase,
    GameSession,
    HandSnapshot,
)
from punto81.domain.models.money import chips
from punto81.domain.policies.cpu import choose_discards
from punto81.domain.rules.betting import BetAction, BetActionKind
from punto81.domain.rules.hand_evaluator import HandRank, evaluate


@dataclass(frozen=True, slots=True)
class DemoEvent:
    """One step of the demo, useful for the UI to render a recap."""

    label: str
    snapshot: HandSnapshot


def _human_first_action(snapshot: HandSnapshot) -> BetAction:
    """Pick a sensible human action for the demo.

    Calls whatever the CPU opened with as long as the hand is at least a
    pair; folds otherwise unless the bet is tiny.
    """
    assert snapshot.human_hand is not None
    evaluation = evaluate(snapshot.human_hand)
    to_call = int(snapshot.round_state.current_bet) - int(snapshot.round_state.human_committed)
    if to_call == 0:
        return BetAction(BetActionKind.CHECK)
    if evaluation.rank >= HandRank.PAIR or to_call <= 5:
        return BetAction(BetActionKind.CALL)
    return BetAction(BetActionKind.FOLD)


def _human_second_action(snapshot: HandSnapshot) -> BetAction:
    """Open the second round: bet small with strong hands, check otherwise."""
    assert snapshot.human_hand is not None
    evaluation = evaluate(snapshot.human_hand)
    if evaluation.rank >= HandRank.TWO_PAIR:
        return BetAction(BetActionKind.BET, chips(10))
    return BetAction(BetActionKind.CHECK)


def play_demo_hand(session: GameSession) -> Iterable[DemoEvent]:
    """Play exactly one demo hand on the given session.

    Yields ``DemoEvent`` items so a UI can render each step.
    """
    snapshot = session.start_hand()
    yield DemoEvent("reparto y apuesta inicial CPU", snapshot)
    if snapshot.phase is GamePhase.GAME_OVER:
        return

    action = _human_first_action(snapshot)
    snapshot = session.human_first_bet(action)
    yield DemoEvent(f"jugador {action.kind.value}", snapshot)
    if snapshot.phase in {GamePhase.HAND_OVER, GamePhase.GAME_OVER}:
        return

    assert snapshot.human_hand is not None
    discards = choose_discards(snapshot.human_hand)
    snapshot = session.human_discard(discards)
    yield DemoEvent(f"descarte humano: {len(discards)}", snapshot)

    action2 = _human_second_action(snapshot)
    snapshot = session.human_second_bet(action2)
    yield DemoEvent(f"jugador {action2.kind.value} en 2.ª ronda", snapshot)


def play_demo_game(session: GameSession, max_hands: int = 12) -> list[DemoEvent]:
    """Play hands until somebody busts or ``max_hands`` is reached."""
    events: list[DemoEvent] = []
    for _ in range(max_hands):
        snapshot = session.snapshot
        if snapshot.human.is_busted or snapshot.cpu.is_busted:
            break
        for event in play_demo_hand(session):
            events.append(event)
        if events and events[-1].snapshot.phase is GamePhase.GAME_OVER:
            break
    return events
