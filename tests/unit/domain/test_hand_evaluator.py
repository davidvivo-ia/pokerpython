"""Tests for the hand evaluator."""

from __future__ import annotations

from punto81.domain.models.card import Card, Rank, Suit
from punto81.domain.models.hand import Hand
from punto81.domain.rules.hand_evaluator import HandRank, evaluate


def _hand(*pairs: tuple[Rank, Suit]) -> Hand:
    return Hand.of(tuple(Card(rank=r, suit=s) for r, s in pairs))


def test_straight_flush() -> None:
    hand = _hand(
        (Rank.TEN, Suit.SPADES),
        (Rank.JACK, Suit.SPADES),
        (Rank.QUEEN, Suit.SPADES),
        (Rank.KING, Suit.SPADES),
        (Rank.ACE, Suit.SPADES),
    )
    assert evaluate(hand).rank is HandRank.STRAIGHT_FLUSH


def test_wheel_straight_flush() -> None:
    hand = _hand(
        (Rank.ACE, Suit.HEARTS),
        (Rank.TWO, Suit.HEARTS),
        (Rank.THREE, Suit.HEARTS),
        (Rank.FOUR, Suit.HEARTS),
        (Rank.FIVE, Suit.HEARTS),
    )
    evaluation = evaluate(hand)
    assert evaluation.rank is HandRank.STRAIGHT_FLUSH
    assert evaluation.tiebreakers == (5,)


def test_four_of_a_kind_beats_full_house() -> None:
    quads = _hand(
        (Rank.KING, Suit.CLUBS),
        (Rank.KING, Suit.DIAMONDS),
        (Rank.KING, Suit.HEARTS),
        (Rank.KING, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    full = _hand(
        (Rank.QUEEN, Suit.CLUBS),
        (Rank.QUEEN, Suit.DIAMONDS),
        (Rank.QUEEN, Suit.HEARTS),
        (Rank.JACK, Suit.SPADES),
        (Rank.JACK, Suit.CLUBS),
    )
    assert evaluate(quads) > evaluate(full)
    assert evaluate(quads).rank is HandRank.FOUR_OF_A_KIND
    assert evaluate(full).rank is HandRank.FULL_HOUSE


def test_flush() -> None:
    hand = _hand(
        (Rank.TWO, Suit.HEARTS),
        (Rank.SIX, Suit.HEARTS),
        (Rank.NINE, Suit.HEARTS),
        (Rank.JACK, Suit.HEARTS),
        (Rank.KING, Suit.HEARTS),
    )
    assert evaluate(hand).rank is HandRank.FLUSH


def test_straight() -> None:
    hand = _hand(
        (Rank.SIX, Suit.HEARTS),
        (Rank.SEVEN, Suit.CLUBS),
        (Rank.EIGHT, Suit.HEARTS),
        (Rank.NINE, Suit.DIAMONDS),
        (Rank.TEN, Suit.SPADES),
    )
    evaluation = evaluate(hand)
    assert evaluation.rank is HandRank.STRAIGHT
    assert evaluation.tiebreakers == (10,)


def test_wheel_straight_low() -> None:
    hand = _hand(
        (Rank.ACE, Suit.HEARTS),
        (Rank.TWO, Suit.CLUBS),
        (Rank.THREE, Suit.DIAMONDS),
        (Rank.FOUR, Suit.SPADES),
        (Rank.FIVE, Suit.HEARTS),
    )
    evaluation = evaluate(hand)
    assert evaluation.rank is HandRank.STRAIGHT
    assert evaluation.tiebreakers == (5,)


def test_three_of_a_kind() -> None:
    hand = _hand(
        (Rank.QUEEN, Suit.CLUBS),
        (Rank.QUEEN, Suit.DIAMONDS),
        (Rank.QUEEN, Suit.HEARTS),
        (Rank.SEVEN, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    assert evaluate(hand).rank is HandRank.THREE_OF_A_KIND


def test_two_pair_uses_high_pair_first() -> None:
    hand = _hand(
        (Rank.ACE, Suit.CLUBS),
        (Rank.ACE, Suit.DIAMONDS),
        (Rank.KING, Suit.HEARTS),
        (Rank.KING, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    evaluation = evaluate(hand)
    assert evaluation.rank is HandRank.TWO_PAIR
    assert evaluation.tiebreakers == (14, 13, 2)


def test_pair() -> None:
    hand = _hand(
        (Rank.SEVEN, Suit.CLUBS),
        (Rank.SEVEN, Suit.DIAMONDS),
        (Rank.KING, Suit.HEARTS),
        (Rank.FIVE, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    evaluation = evaluate(hand)
    assert evaluation.rank is HandRank.PAIR
    assert evaluation.tiebreakers == (7, 13, 5, 2)


def test_high_card() -> None:
    hand = _hand(
        (Rank.ACE, Suit.CLUBS),
        (Rank.KING, Suit.DIAMONDS),
        (Rank.QUEEN, Suit.HEARTS),
        (Rank.JACK, Suit.SPADES),
        (Rank.NINE, Suit.CLUBS),
    )
    evaluation = evaluate(hand)
    assert evaluation.rank is HandRank.HIGH_CARD
    assert evaluation.tiebreakers == (14, 13, 12, 11, 9)


def test_label_es_for_all_ranks() -> None:
    for rank in HandRank:
        assert isinstance(rank.label_es, str)
        assert rank.label_es != ""
