"""Tests for the immutable Deck."""

from __future__ import annotations

import pytest

from punto81.domain.models.deck import Deck, EmptyDeckError
from punto81.domain.ports.rng import Rng


def test_ordered_deck_has_52_unique_cards() -> None:
    deck = Deck.ordered()
    assert deck.remaining == 52
    assert len(set(deck.cards)) == 52


def test_shuffled_deck_keeps_all_cards(rng: Rng) -> None:
    shuffled = Deck.shuffled(rng)
    assert shuffled.remaining == 52
    assert set(shuffled.cards) == set(Deck.ordered().cards)


def test_draw_advances_cursor_and_returns_cards() -> None:
    deck = Deck.ordered()
    new_deck, drawn = deck.draw(5)
    assert len(drawn) == 5
    assert new_deck.cursor == 5
    assert new_deck.remaining == 47


def test_draw_raises_when_too_many() -> None:
    deck = Deck.ordered()
    with pytest.raises(EmptyDeckError):
        deck.draw(53)


def test_draw_rejects_negative() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        Deck.ordered().draw(-1)


def test_consecutive_draws_share_no_cards() -> None:
    deck = Deck.ordered()
    d1, first = deck.draw(5)
    _, second = d1.draw(5)
    assert set(first).isdisjoint(set(second))
