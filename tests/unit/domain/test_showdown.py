"""Tests for showdown resolution."""

from __future__ import annotations

from punto81.domain.models.card import Card, Rank, Suit
from punto81.domain.models.hand import Hand
from punto81.domain.rules.showdown import Winner, resolve


def _hand(*pairs: tuple[Rank, Suit]) -> Hand:
    return Hand.of(tuple(Card(rank=r, suit=s) for r, s in pairs))


def test_human_wins_when_eval_higher() -> None:
    human = _hand(
        (Rank.QUEEN, Suit.CLUBS),
        (Rank.QUEEN, Suit.DIAMONDS),
        (Rank.QUEEN, Suit.HEARTS),
        (Rank.SEVEN, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    cpu = _hand(
        (Rank.SEVEN, Suit.CLUBS),
        (Rank.SEVEN, Suit.DIAMONDS),
        (Rank.KING, Suit.HEARTS),
        (Rank.FIVE, Suit.SPADES),
        (Rank.TWO, Suit.DIAMONDS),
    )
    assert resolve(human, cpu).winner is Winner.HUMAN


def test_cpu_wins_when_eval_higher() -> None:
    human = _hand(
        (Rank.SEVEN, Suit.CLUBS),
        (Rank.SEVEN, Suit.DIAMONDS),
        (Rank.KING, Suit.HEARTS),
        (Rank.FIVE, Suit.SPADES),
        (Rank.TWO, Suit.DIAMONDS),
    )
    cpu = _hand(
        (Rank.QUEEN, Suit.CLUBS),
        (Rank.QUEEN, Suit.DIAMONDS),
        (Rank.QUEEN, Suit.HEARTS),
        (Rank.SEVEN, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    assert resolve(human, cpu).winner is Winner.CPU


def test_tie_when_identical_evaluation() -> None:
    human = _hand(
        (Rank.QUEEN, Suit.CLUBS),
        (Rank.QUEEN, Suit.DIAMONDS),
        (Rank.KING, Suit.HEARTS),
        (Rank.SEVEN, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    cpu = _hand(
        (Rank.QUEEN, Suit.HEARTS),
        (Rank.QUEEN, Suit.SPADES),
        (Rank.KING, Suit.CLUBS),
        (Rank.SEVEN, Suit.DIAMONDS),
        (Rank.TWO, Suit.DIAMONDS),
    )
    assert resolve(human, cpu).winner is Winner.TIE
