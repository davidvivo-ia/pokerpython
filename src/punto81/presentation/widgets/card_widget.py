"""Static widget rendering an ASCII card."""

from __future__ import annotations

from textual.widgets import Static

from punto81.domain.models.card import Card


def _card_text(card: Card | None, *, hidden: bool) -> str:
    if hidden or card is None:
        return (
            "╭─────────╮\n"
            "│╳╳╳╳╳╳╳╳╳│\n"
            "│╳╳╳╳╳╳╳╳╳│\n"
            "│╳╳╳╳╳╳╳╳╳│\n"
            "│╳╳╳╳╳╳╳╳╳│\n"
            "│╳╳╳╳╳╳╳╳╳│\n"
            "╰─────────╯"
        )
    rank = card.rank.short
    glyph = card.suit.glyph
    left = rank.ljust(2)
    right = rank.rjust(2)
    return (
        "╭─────────╮\n"
        f"│{left}       │\n"
        "│         │\n"
        f"│    {glyph}    │\n"
        "│         │\n"
        f"│       {right}│\n"
        "╰─────────╯"
    )


class CardWidget(Static):
    """A single 11×7 ASCII card."""

    DEFAULT_CSS = """
    CardWidget {
        width: 13;
        height: 7;
        content-align: center middle;
    }
    """

    def __init__(self, card: Card | None = None, *, hidden: bool = False) -> None:
        super().__init__(_card_text(card, hidden=hidden))
        self._card = card
        self._hidden = hidden
        if card is not None and not hidden:
            self.styles.color = "#E25C5C" if card.suit.is_red else "#DCE5DE"

    def update_card(self, card: Card | None, *, hidden: bool = False) -> None:
        """Replace the card displayed by this widget."""
        self._card = card
        self._hidden = hidden
        self.update(_card_text(card, hidden=hidden))
        if card is not None and not hidden:
            self.styles.color = "#E25C5C" if card.suit.is_red else "#DCE5DE"
        else:
            self.styles.color = "#3E5147"
