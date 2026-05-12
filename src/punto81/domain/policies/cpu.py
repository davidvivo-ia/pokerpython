"""CPU decision policies for betting and drawing.

The CPU is a pure function of (its own hand, current round state, RNG).
Splitting it into two policies — betting and drawing — keeps it
testable and easy to tune.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Final

from punto81.domain.models.card import Rank
from punto81.domain.models.hand import Hand
from punto81.domain.models.money import ZERO_CHIPS, Chips, chips
from punto81.domain.ports.rng import Rng
from punto81.domain.rules.hand_evaluator import HandRank, evaluate


class CpuActionKind(Enum):
    """High-level CPU intention towards the human's bet."""

    FOLD = "fold"
    CALL = "call"
    RAISE = "raise"


@dataclass(frozen=True, slots=True)
class CpuResponse:
    """A CPU response to a human action.

    Attributes:
        kind: fold / call / raise.
        raise_amount: extra chips on top of a call. Zero unless ``RAISE``.
    """

    kind: CpuActionKind
    raise_amount: Chips = ZERO_CHIPS


_OPEN_BET_FLOOR: Final[dict[HandRank, tuple[int, int]]] = {
    HandRank.HIGH_CARD: (1, 4),
    HandRank.PAIR: (3, 8),
    HandRank.TWO_PAIR: (5, 12),
    HandRank.THREE_OF_A_KIND: (8, 18),
    HandRank.STRAIGHT: (10, 22),
    HandRank.FLUSH: (10, 22),
    HandRank.FULL_HOUSE: (15, 30),
    HandRank.FOUR_OF_A_KIND: (20, 40),
    HandRank.STRAIGHT_FLUSH: (25, 50),
}

_BLUFF_PROBABILITY: Final[float] = 0.18


def open_bet(hand: Hand, available: Chips, rng: Rng) -> Chips:
    """Pick the chips the CPU bets to open the first round.

    Args:
        hand: the CPU's hand pre-draw.
        available: maximum chips the CPU can afford.
        rng: random source.

    Returns:
        The chip amount to bet, capped at ``available``. A small amount
        is always allowed; with low probability the CPU bluffs by
        betting as if its hand were a pair.
    """
    evaluation = evaluate(hand)
    floor, ceiling = _OPEN_BET_FLOOR[evaluation.rank]
    if evaluation.rank is HandRank.HIGH_CARD and rng.random() < _BLUFF_PROBABILITY:
        floor, ceiling = _OPEN_BET_FLOOR[HandRank.PAIR]
    amount = rng.randint(floor, ceiling)
    capped = min(amount, int(available))
    return chips(max(1, capped)) if available > 0 else chips(0)


def respond_to_bet(
    hand: Hand,
    to_call: Chips,
    cpu_bankroll: Chips,
    pot: Chips,
    rng: Rng,
) -> CpuResponse:
    """Decide how the CPU reacts to a human bet/raise.

    Args:
        hand: the CPU's hand after the draw.
        to_call: chips the CPU must pay to stay in.
        cpu_bankroll: chips the CPU currently has.
        pot: chips already in the pot (decision uses pot odds loosely).
        rng: random source.

    Returns:
        A ``CpuResponse``.
    """
    evaluation = evaluate(hand)
    rank = evaluation.rank
    affordable = int(cpu_bankroll) >= int(to_call)

    if not affordable:
        return CpuResponse(CpuActionKind.FOLD)

    if rank >= HandRank.STRAIGHT:
        if rng.random() < 0.55 and int(cpu_bankroll) > int(to_call) + 5:
            extra = rng.randint(5, max(5, min(20, int(cpu_bankroll) - int(to_call))))
            return CpuResponse(CpuActionKind.RAISE, chips(extra))
        return CpuResponse(CpuActionKind.CALL)

    if rank >= HandRank.TWO_PAIR:
        if int(to_call) <= int(pot) // 2 or rng.random() < 0.7:
            return CpuResponse(CpuActionKind.CALL)
        return CpuResponse(CpuActionKind.FOLD)

    if rank == HandRank.PAIR:
        if int(to_call) <= 8 or rng.random() < 0.45:
            return CpuResponse(CpuActionKind.CALL)
        return CpuResponse(CpuActionKind.FOLD)

    if int(to_call) == 0:
        return CpuResponse(CpuActionKind.CALL)
    if rng.random() < _BLUFF_PROBABILITY:
        return CpuResponse(CpuActionKind.CALL)
    return CpuResponse(CpuActionKind.FOLD)


def _has_four_to_flush(hand: Hand) -> tuple[int, ...] | None:
    suits = [card.suit for card in hand.cards]
    counter = Counter(suits)
    for suit, count in counter.items():
        if count == 4:
            return tuple(index for index, card in enumerate(hand.cards) if card.suit != suit)
    return None


def _has_open_ended_straight(hand: Hand) -> tuple[int, ...] | None:
    values = sorted({int(card.rank) for card in hand.cards})
    if len(values) < 4:
        return None
    for start in range(len(values) - 3):
        window = values[start : start + 4]
        if window[-1] - window[0] == 3:
            kept = set(window)
            return tuple(
                index for index, card in enumerate(hand.cards) if int(card.rank) not in kept
            )
    return None


def choose_discards(hand: Hand) -> tuple[int, ...]:
    """Return the indices the CPU should discard (up to three).

    Strategy preference, in order:

    1. Hands rated straight-or-better: keep everything (return ``()``).
    2. Three of a kind: discard the two kickers.
    3. Two pair: discard the lone kicker.
    4. One pair: discard the three non-pair cards.
    5. Four-card flush draw: discard the off-suit card.
    6. Open-ended straight draw: discard the one card not in the run.
    7. Otherwise: keep the highest card and discard the other four
       (capped at 3 by the rules of the game).

    Args:
        hand: the CPU's pre-draw hand.

    Returns:
        Tuple of card indices to replace, sorted ascending.
    """
    evaluation = evaluate(hand)
    if evaluation.rank >= HandRank.STRAIGHT:
        return ()

    values: list[int] = [int(card.rank) for card in hand.cards]
    counts = Counter(values)

    if evaluation.rank is HandRank.THREE_OF_A_KIND:
        trips_value = next(value for value, count in counts.items() if count == 3)
        return tuple(
            sorted(index for index, card in enumerate(hand.cards) if int(card.rank) != trips_value)
        )

    if evaluation.rank is HandRank.TWO_PAIR:
        pair_values = {value for value, count in counts.items() if count == 2}
        return tuple(
            sorted(
                index for index, card in enumerate(hand.cards) if int(card.rank) not in pair_values
            )
        )

    if evaluation.rank is HandRank.PAIR:
        pair_value = next(value for value, count in counts.items() if count == 2)
        return tuple(
            sorted(index for index, card in enumerate(hand.cards) if int(card.rank) != pair_value)
        )

    flush_draw = _has_four_to_flush(hand)
    if flush_draw is not None:
        return flush_draw

    straight_draw = _has_open_ended_straight(hand)
    if straight_draw is not None and len(straight_draw) == 1:
        return straight_draw

    # High-card hand: keep the highest card, discard up to three of the rest.
    ranked_indices = sorted(range(5), key=lambda i: int(hand.cards[i].rank), reverse=True)
    keepers = {ranked_indices[0]}
    if int(hand.cards[ranked_indices[1]].rank) >= int(Rank.QUEEN):
        keepers.add(ranked_indices[1])
    return tuple(sorted(index for index in range(5) if index not in keepers))[:3]
