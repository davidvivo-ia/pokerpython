"""Tests for the CPU decision policies."""

from __future__ import annotations

from punto81.domain.models.card import Card, Rank, Suit
from punto81.domain.models.hand import Hand
from punto81.domain.models.money import chips
from punto81.domain.policies.cpu import (
    CpuActionKind,
    choose_discards,
    open_bet,
    respond_to_bet,
)
from punto81.domain.ports.rng import Rng


def _hand(*pairs: tuple[Rank, Suit]) -> Hand:
    return Hand.of(tuple(Card(rank=r, suit=s) for r, s in pairs))


def test_open_bet_within_band(rng: Rng) -> None:
    hand = _hand(
        (Rank.SEVEN, Suit.CLUBS),
        (Rank.SEVEN, Suit.DIAMONDS),
        (Rank.KING, Suit.HEARTS),
        (Rank.FIVE, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    bet = open_bet(hand, chips(100), rng)
    assert 1 <= bet <= 100


def test_open_bet_caps_at_available(rng: Rng) -> None:
    hand = _hand(
        (Rank.KING, Suit.CLUBS),
        (Rank.KING, Suit.DIAMONDS),
        (Rank.KING, Suit.HEARTS),
        (Rank.KING, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    bet = open_bet(hand, chips(3), rng)
    assert bet <= 3


def test_open_bet_returns_zero_when_broke(rng: Rng) -> None:
    hand = _hand(
        (Rank.SEVEN, Suit.CLUBS),
        (Rank.SEVEN, Suit.DIAMONDS),
        (Rank.KING, Suit.HEARTS),
        (Rank.FIVE, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    assert open_bet(hand, chips(0), rng) == 0


def test_respond_strong_hand_calls_or_raises(rng: Rng) -> None:
    hand = _hand(
        (Rank.TEN, Suit.SPADES),
        (Rank.JACK, Suit.SPADES),
        (Rank.QUEEN, Suit.SPADES),
        (Rank.KING, Suit.SPADES),
        (Rank.ACE, Suit.SPADES),
    )
    response = respond_to_bet(hand, chips(20), chips(200), chips(40), rng)
    assert response.kind in {CpuActionKind.CALL, CpuActionKind.RAISE}


def test_respond_folds_when_cannot_afford(rng: Rng) -> None:
    hand = _hand(
        (Rank.TWO, Suit.SPADES),
        (Rank.FOUR, Suit.CLUBS),
        (Rank.SEVEN, Suit.DIAMONDS),
        (Rank.NINE, Suit.HEARTS),
        (Rank.JACK, Suit.SPADES),
    )
    response = respond_to_bet(hand, chips(50), chips(10), chips(20), rng)
    assert response.kind is CpuActionKind.FOLD


def test_respond_pair_calls_small_bet(rng: Rng) -> None:
    hand = _hand(
        (Rank.SEVEN, Suit.CLUBS),
        (Rank.SEVEN, Suit.DIAMONDS),
        (Rank.KING, Suit.HEARTS),
        (Rank.FIVE, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    response = respond_to_bet(hand, chips(5), chips(100), chips(10), rng)
    assert response.kind is CpuActionKind.CALL


def test_choose_discards_keeps_strong_hand() -> None:
    hand = _hand(
        (Rank.TEN, Suit.SPADES),
        (Rank.JACK, Suit.SPADES),
        (Rank.QUEEN, Suit.SPADES),
        (Rank.KING, Suit.SPADES),
        (Rank.ACE, Suit.SPADES),
    )
    assert choose_discards(hand) == ()


def test_choose_discards_keeps_three_of_a_kind() -> None:
    hand = _hand(
        (Rank.SEVEN, Suit.CLUBS),
        (Rank.SEVEN, Suit.DIAMONDS),
        (Rank.SEVEN, Suit.HEARTS),
        (Rank.KING, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    discards = choose_discards(hand)
    kept_ranks = [hand.cards[i].rank for i in range(5) if i not in discards]
    assert kept_ranks.count(Rank.SEVEN) == 3
    assert len(discards) == 2


def test_choose_discards_keeps_two_pair() -> None:
    hand = _hand(
        (Rank.ACE, Suit.CLUBS),
        (Rank.ACE, Suit.DIAMONDS),
        (Rank.KING, Suit.HEARTS),
        (Rank.KING, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    assert choose_discards(hand) == (0,)


def test_choose_discards_keeps_pair() -> None:
    hand = _hand(
        (Rank.SEVEN, Suit.CLUBS),
        (Rank.SEVEN, Suit.DIAMONDS),
        (Rank.KING, Suit.HEARTS),
        (Rank.FIVE, Suit.SPADES),
        (Rank.TWO, Suit.CLUBS),
    )
    discards = choose_discards(hand)
    assert len(discards) == 3
    assert all(hand.cards[i].rank is not Rank.SEVEN for i in discards)


def test_choose_discards_flush_draw() -> None:
    hand = _hand(
        (Rank.TWO, Suit.HEARTS),
        (Rank.FIVE, Suit.HEARTS),
        (Rank.NINE, Suit.HEARTS),
        (Rank.KING, Suit.HEARTS),
        (Rank.SEVEN, Suit.SPADES),
    )
    discards = choose_discards(hand)
    assert len(discards) == 1
    assert hand.cards[discards[0]].suit is Suit.SPADES


def test_choose_discards_open_ended_straight_draw() -> None:
    hand = _hand(
        (Rank.SIX, Suit.HEARTS),
        (Rank.SEVEN, Suit.CLUBS),
        (Rank.EIGHT, Suit.HEARTS),
        (Rank.NINE, Suit.DIAMONDS),
        (Rank.KING, Suit.SPADES),
    )
    discards = choose_discards(hand)
    assert len(discards) == 1
    assert hand.cards[discards[0]].rank is Rank.KING


def test_choose_discards_high_card_keeps_top() -> None:
    hand = _hand(
        (Rank.TWO, Suit.HEARTS),
        (Rank.FIVE, Suit.CLUBS),
        (Rank.NINE, Suit.DIAMONDS),
        (Rank.JACK, Suit.SPADES),
        (Rank.ACE, Suit.HEARTS),
    )
    discards = choose_discards(hand)
    assert len(discards) <= 3
    kept_indices = [i for i in range(5) if i not in discards]
    kept_ranks = {hand.cards[i].rank for i in kept_indices}
    assert Rank.ACE in kept_ranks
