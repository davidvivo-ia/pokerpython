"""Hypothesis property tests for the hand evaluator."""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from punto81.domain.models.card import Card, Rank, Suit
from punto81.domain.models.hand import Hand
from punto81.domain.rules.hand_evaluator import HandRank, evaluate


def _all_cards() -> list[Card]:
    return [Card(rank=r, suit=s) for r in Rank for s in Suit]


@st.composite
def hands(draw: st.DrawFn) -> Hand:
    cards = draw(st.lists(st.sampled_from(_all_cards()), min_size=5, max_size=5, unique=True))
    return Hand.of(tuple(cards))


@given(hand=hands())
def test_evaluation_rank_is_valid(hand: Hand) -> None:
    evaluation = evaluate(hand)
    assert evaluation.rank in HandRank
    assert all(isinstance(tb, int) for tb in evaluation.tiebreakers)


@given(hand=hands())
def test_evaluation_is_self_equal(hand: Hand) -> None:
    assert evaluate(hand) == evaluate(hand)


@given(a=hands(), b=hands(), c=hands())
def test_evaluation_ordering_is_transitive(a: Hand, b: Hand, c: Hand) -> None:
    ea, eb, ec = evaluate(a), evaluate(b), evaluate(c)
    if ea < eb < ec:
        assert ea < ec


@given(hand=hands())
def test_evaluation_invariant_under_shuffle(hand: Hand) -> None:
    reversed_cards = tuple(reversed(hand.cards))
    rebuilt = Hand.of(reversed_cards)
    assert evaluate(rebuilt) == evaluate(hand)
