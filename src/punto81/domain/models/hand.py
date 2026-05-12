"""The 5-card immutable poker hand."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from punto81.domain.models.card import Card


class InvalidHandError(ValueError):
    """Raised when a hand cannot be constructed from the given cards."""


@dataclass(frozen=True, slots=True)
class Hand:
    """Exactly five distinct cards, order-insensitive but stored sorted."""

    cards: tuple[Card, Card, Card, Card, Card]

    def __post_init__(self) -> None:
        if len(self.cards) != 5:
            raise InvalidHandError(f"a hand must contain 5 cards, got {len(self.cards)}")
        if len(set(self.cards)) != 5:
            raise InvalidHandError("a hand cannot contain duplicate cards")

    @classmethod
    def of(cls, cards: tuple[Card, ...]) -> Hand:
        """Build a sorted hand from a tuple of cards.

        Args:
            cards: tuple of exactly five distinct cards in any order.

        Returns:
            A new ``Hand`` whose internal storage is sorted ascending by
            ``Card.sort_key`` so display is deterministic.
        """
        if len(cards) != 5:
            raise InvalidHandError(f"a hand must contain 5 cards, got {len(cards)}")
        sorted_cards = tuple(sorted(cards, key=lambda c: c.sort_key))
        return cls(
            (
                sorted_cards[0],
                sorted_cards[1],
                sorted_cards[2],
                sorted_cards[3],
                sorted_cards[4],
            )
        )

    def replace(self, positions: tuple[int, ...], new_cards: tuple[Card, ...]) -> Hand:
        """Return a new hand with cards at ``positions`` swapped for ``new_cards``.

        Args:
            positions: indices (0-based) of cards to discard. Must be sorted
                ascending and unique. Length must equal ``len(new_cards)``.
            new_cards: replacement cards.

        Returns:
            A new sorted ``Hand``.

        Raises:
            InvalidHandError: if positions are out of range or counts mismatch.
        """
        if len(positions) != len(new_cards):
            raise InvalidHandError("positions and new_cards must match in length")
        if any(p < 0 or p > 4 for p in positions):
            raise InvalidHandError("positions must be in [0, 4]")
        if len(set(positions)) != len(positions):
            raise InvalidHandError("positions must be unique")
        replaced = list(self.cards)
        for index, new_card in zip(positions, new_cards, strict=True):
            replaced[index] = new_card
        return Hand.of(tuple(replaced))

    def __iter__(self) -> Iterator[Card]:
        return iter(self.cards)

    def __len__(self) -> int:
        return 5

    def __str__(self) -> str:
        return " ".join(str(card) for card in self.cards)
