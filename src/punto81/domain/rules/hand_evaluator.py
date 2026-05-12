"""Pure 5-card poker hand evaluator.

Produces a totally ordered ``Evaluation`` for any ``Hand`` so two
evaluations can be compared with ``<`` and ``==``.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import IntEnum
from typing import Final

from punto81.domain.models.card import Rank
from punto81.domain.models.hand import Hand


class HandRank(IntEnum):
    """The nine traditional poker hand categories, weakest to strongest."""

    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9

    @property
    def label_es(self) -> str:
        """Spanish display label for the rank."""
        return _LABELS_ES[self]


_LABELS_ES: Final[dict[HandRank, str]] = {
    HandRank.HIGH_CARD: "Carta alta",
    HandRank.PAIR: "Pareja",
    HandRank.TWO_PAIR: "Doble pareja",
    HandRank.THREE_OF_A_KIND: "Trío",
    HandRank.STRAIGHT: "Escalera",
    HandRank.FLUSH: "Color",
    HandRank.FULL_HOUSE: "Full",
    HandRank.FOUR_OF_A_KIND: "Póker",
    HandRank.STRAIGHT_FLUSH: "Escalera de color",
}

_WHEEL: Final[frozenset[int]] = frozenset({2, 3, 4, 5, 14})


@dataclass(frozen=True, slots=True, order=True)
class Evaluation:
    """A totally ordered hand evaluation.

    The first field is the ``HandRank``; the second is a tiebreaker
    tuple. Two evaluations compare by category first, then lexicographic
    tiebreakers (highest first).
    """

    rank: HandRank
    tiebreakers: tuple[int, ...]

    @property
    def label_es(self) -> str:
        """Spanish display label for the evaluation."""
        return self.rank.label_es


def _rank_counts(values: tuple[int, ...]) -> list[tuple[int, int]]:
    counter = Counter(values)
    return sorted(counter.items(), key=lambda kv: (-kv[1], -kv[0]))


def _is_flush(suits: tuple[str, ...]) -> bool:
    return len(set(suits)) == 1


def _straight_high(values: tuple[int, ...]) -> int | None:
    unique = sorted(set(values))
    if len(unique) != 5:
        return None
    if unique[-1] - unique[0] == 4:
        return unique[-1]
    if set(unique) == _WHEEL:
        return Rank.FIVE.value
    return None


def evaluate(hand: Hand) -> Evaluation:
    """Evaluate a 5-card hand into a totally ordered ``Evaluation``.

    Args:
        hand: the hand to evaluate.

    Returns:
        An ``Evaluation`` whose ``rank`` is the category and whose
        ``tiebreakers`` resolve ties between two hands of the same
        category (e.g. higher pair wins).
    """
    values: tuple[int, ...] = tuple(int(card.rank) for card in hand.cards)
    suits: tuple[str, ...] = tuple(card.suit.value for card in hand.cards)

    flush = _is_flush(suits)
    straight_high = _straight_high(values)
    groups = _rank_counts(values)
    counts = tuple(count for _, count in groups)
    ordered_values = tuple(value for value, _ in groups)

    if flush and straight_high is not None:
        return Evaluation(HandRank.STRAIGHT_FLUSH, (straight_high,))
    if counts[0] == 4:
        quad, kicker = ordered_values[0], ordered_values[1]
        return Evaluation(HandRank.FOUR_OF_A_KIND, (quad, kicker))
    if counts[0] == 3 and counts[1] == 2:
        trips, pair = ordered_values[0], ordered_values[1]
        return Evaluation(HandRank.FULL_HOUSE, (trips, pair))
    if flush:
        return Evaluation(HandRank.FLUSH, tuple(sorted(values, reverse=True)))
    if straight_high is not None:
        return Evaluation(HandRank.STRAIGHT, (straight_high,))
    if counts[0] == 3:
        trips = ordered_values[0]
        kickers = tuple(sorted(ordered_values[1:], reverse=True))
        return Evaluation(HandRank.THREE_OF_A_KIND, (trips, *kickers))
    if counts[0] == 2 and counts[1] == 2:
        high_pair = max(ordered_values[0], ordered_values[1])
        low_pair = min(ordered_values[0], ordered_values[1])
        kicker = ordered_values[2]
        return Evaluation(HandRank.TWO_PAIR, (high_pair, low_pair, kicker))
    if counts[0] == 2:
        pair = ordered_values[0]
        kickers = tuple(sorted(ordered_values[1:], reverse=True))
        return Evaluation(HandRank.PAIR, (pair, *kickers))
    return Evaluation(HandRank.HIGH_CARD, tuple(sorted(values, reverse=True)))
