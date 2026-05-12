"""Tests for Hand construction and replacement."""

from __future__ import annotations

import pytest

from punto81.domain.models.card import Card, Rank, Suit
from punto81.domain.models.hand import Hand, InvalidHandError


def _h(*ranks_and_suits: tuple[Rank, Suit]) -> tuple[Card, ...]:
    return tuple(Card(rank=r, suit=s) for r, s in ranks_and_suits)


def test_hand_of_sorts_by_sort_key() -> None:
    cards = _h(
        (Rank.ACE, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
        (Rank.KING, Suit.HEARTS),
        (Rank.FIVE, Suit.DIAMONDS),
        (Rank.JACK, Suit.CLUBS),
    )
    hand = Hand.of(cards)
    ranks = [card.rank for card in hand.cards]
    assert ranks == [Rank.TWO, Rank.FIVE, Rank.JACK, Rank.KING, Rank.ACE]


def test_hand_rejects_wrong_size() -> None:
    cards = _h(
        (Rank.ACE, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
        (Rank.KING, Suit.HEARTS),
    )
    with pytest.raises(InvalidHandError):
        Hand.of(cards)


def test_hand_rejects_duplicates() -> None:
    cards = _h(
        (Rank.ACE, Suit.SPADES),
        (Rank.ACE, Suit.SPADES),
        (Rank.KING, Suit.HEARTS),
        (Rank.FIVE, Suit.DIAMONDS),
        (Rank.JACK, Suit.CLUBS),
    )
    with pytest.raises(InvalidHandError):
        Hand.of(cards)


def test_hand_replace_swaps_cards() -> None:
    hand = Hand.of(
        _h(
            (Rank.TWO, Suit.CLUBS),
            (Rank.FIVE, Suit.DIAMONDS),
            (Rank.JACK, Suit.CLUBS),
            (Rank.KING, Suit.HEARTS),
            (Rank.ACE, Suit.SPADES),
        )
    )
    replacements = _h(
        (Rank.THREE, Suit.CLUBS),
        (Rank.FOUR, Suit.CLUBS),
    )
    new_hand = hand.replace((0, 1), replacements)
    ranks = [card.rank for card in new_hand.cards]
    assert ranks == [Rank.THREE, Rank.FOUR, Rank.JACK, Rank.KING, Rank.ACE]


def test_hand_replace_rejects_bad_positions() -> None:
    hand = Hand.of(
        _h(
            (Rank.TWO, Suit.CLUBS),
            (Rank.FIVE, Suit.DIAMONDS),
            (Rank.JACK, Suit.CLUBS),
            (Rank.KING, Suit.HEARTS),
            (Rank.ACE, Suit.SPADES),
        )
    )
    with pytest.raises(InvalidHandError):
        hand.replace((0, 0), _h((Rank.THREE, Suit.CLUBS), (Rank.FOUR, Suit.CLUBS)))
    with pytest.raises(InvalidHandError):
        hand.replace(
            (5,),
            _h(
                (Rank.THREE, Suit.CLUBS),
            ),
        )
    with pytest.raises(InvalidHandError):
        hand.replace(
            (0, 1),
            _h(
                (Rank.THREE, Suit.CLUBS),
            ),
        )


def test_hand_iter_and_len() -> None:
    hand = Hand.of(
        _h(
            (Rank.TWO, Suit.CLUBS),
            (Rank.FIVE, Suit.DIAMONDS),
            (Rank.JACK, Suit.CLUBS),
            (Rank.KING, Suit.HEARTS),
            (Rank.ACE, Suit.SPADES),
        )
    )
    assert len(hand) == 5
    assert list(hand)[-1].rank is Rank.ACE
    assert str(hand).startswith("2♣")
