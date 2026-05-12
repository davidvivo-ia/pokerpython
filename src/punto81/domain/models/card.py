"""Cards, suits and ranks."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Final


class Suit(Enum):
    """The four French-deck suits."""

    CLUBS = "C"
    DIAMONDS = "D"
    HEARTS = "H"
    SPADES = "S"

    @property
    def sort_key(self) -> int:
        """Stable ordering key for deterministic sorts (clubs first)."""
        return _SUIT_ORDER[self]

    @property
    def glyph(self) -> str:
        """Return the Unicode glyph for the suit."""
        return _SUIT_GLYPHS[self]

    @property
    def is_red(self) -> bool:
        """Whether the suit is rendered in red on a traditional deck."""
        return self in {Suit.HEARTS, Suit.DIAMONDS}


_SUIT_GLYPHS: Final[dict[Suit, str]] = {
    Suit.CLUBS: "♣",
    Suit.DIAMONDS: "♦",
    Suit.HEARTS: "♥",
    Suit.SPADES: "♠",
}

_SUIT_ORDER: Final[dict[Suit, int]] = {
    Suit.CLUBS: 0,
    Suit.DIAMONDS: 1,
    Suit.HEARTS: 2,
    Suit.SPADES: 3,
}


class Rank(IntEnum):
    """Card ranks with their numeric value (deuce-low, ace-high)."""

    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

    @property
    def short(self) -> str:
        """Single- or double-character label used by widgets."""
        return _RANK_SHORT[self]


_RANK_SHORT: Final[dict[Rank, str]] = {
    Rank.TWO: "2",
    Rank.THREE: "3",
    Rank.FOUR: "4",
    Rank.FIVE: "5",
    Rank.SIX: "6",
    Rank.SEVEN: "7",
    Rank.EIGHT: "8",
    Rank.NINE: "9",
    Rank.TEN: "10",
    Rank.JACK: "J",
    Rank.QUEEN: "Q",
    Rank.KING: "K",
    Rank.ACE: "A",
}


@dataclass(frozen=True, slots=True)
class Card:
    """An immutable playing card."""

    rank: Rank
    suit: Suit

    def __str__(self) -> str:
        return f"{self.rank.short}{self.suit.glyph}"

    @property
    def sort_key(self) -> tuple[int, int]:
        """Deterministic ordering: by rank ascending, suit alphabetical."""
        return (int(self.rank), self.suit.sort_key)
