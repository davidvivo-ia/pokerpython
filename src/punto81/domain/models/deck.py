"""Immutable 52-card deck with a draw cursor."""

from __future__ import annotations

from dataclasses import dataclass

from punto81.domain.models.card import Card, Rank, Suit
from punto81.domain.ports.rng import Rng


class EmptyDeckError(RuntimeError):
    """Raised when more cards are drawn than the deck contains."""


def _ordered_deck() -> tuple[Card, ...]:
    return tuple(Card(rank=rank, suit=suit) for rank in Rank for suit in Suit)


@dataclass(frozen=True, slots=True)
class Deck:
    """A standard 52-card deck with an immutable draw cursor.

    Each ``draw`` returns a new ``Deck`` with the cursor advanced. The
    underlying tuple is shared (frozen).
    """

    cards: tuple[Card, ...]
    cursor: int = 0

    @classmethod
    def shuffled(cls, rng: Rng) -> Deck:
        """Return a fresh deck shuffled by the injected RNG."""
        base = _ordered_deck()
        permutation = rng.shuffle_indices(len(base))
        return cls(cards=tuple(base[index] for index in permutation), cursor=0)

    @classmethod
    def ordered(cls) -> Deck:
        """Return a fresh deck in canonical Rank × Suit order (tests only)."""
        return cls(cards=_ordered_deck(), cursor=0)

    @property
    def remaining(self) -> int:
        """Number of cards still drawable."""
        return len(self.cards) - self.cursor

    def draw(self, count: int) -> tuple[Deck, tuple[Card, ...]]:
        """Draw ``count`` cards.

        Args:
            count: number of cards to draw.

        Returns:
            A pair ``(new_deck, drawn_cards)``.

        Raises:
            EmptyDeckError: if ``count`` exceeds the cards remaining.
            ValueError: if ``count`` is negative.
        """
        if count < 0:
            raise ValueError("count must be non-negative")
        if count > self.remaining:
            raise EmptyDeckError(f"requested {count} cards but only {self.remaining} remain")
        drawn = self.cards[self.cursor : self.cursor + count]
        return (
            Deck(cards=self.cards, cursor=self.cursor + count),
            drawn,
        )
