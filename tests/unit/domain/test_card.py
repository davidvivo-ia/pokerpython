"""Tests for cards, ranks and suits."""

from __future__ import annotations

from punto81.domain.models.card import Card, Rank, Suit


def test_rank_short_labels() -> None:
    assert Rank.TWO.short == "2"
    assert Rank.TEN.short == "10"
    assert Rank.JACK.short == "J"
    assert Rank.ACE.short == "A"


def test_suit_glyphs_and_colors() -> None:
    assert Suit.HEARTS.glyph == "♥"
    assert Suit.SPADES.glyph == "♠"
    assert Suit.HEARTS.is_red is True
    assert Suit.CLUBS.is_red is False


def test_card_string_and_sort_key() -> None:
    card = Card(Rank.ACE, Suit.SPADES)
    assert str(card) == "A♠"
    assert card.sort_key == (14, 3)


def test_cards_are_hashable_and_immutable() -> None:
    card = Card(Rank.TWO, Suit.CLUBS)
    deck_set = {card, Card(Rank.TWO, Suit.CLUBS)}
    assert len(deck_set) == 1
