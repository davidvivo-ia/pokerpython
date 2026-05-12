"""Text-mode (non-Textual) renderer used for ``--demo`` and ``--no-tui``."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from punto81.application.use_cases.demo import DemoEvent, play_demo_game
from punto81.application.use_cases.game_session import (
    GamePhase,
    GameSession,
    HandSnapshot,
)
from punto81.domain.models.card import Card
from punto81.domain.models.hand import Hand
from punto81.infrastructure.rng.seeded import SeededRng

_CARD_HEIGHT = 7
_CARD_WIDTH = 11


def _card_lines(card: Card) -> list[str]:
    rank = card.rank.short
    glyph = card.suit.glyph
    left = rank.ljust(2)
    right = rank.rjust(2)
    return [
        "╭─────────╮",
        f"│{left}       │",
        "│         │",
        f"│    {glyph}    │",
        "│         │",
        f"│       {right}│",
        "╰─────────╯",
    ]


def _back_lines() -> list[str]:
    return [
        "╭─────────╮",
        "│╳╳╳╳╳╳╳╳╳│",
        "│╳╳╳╳╳╳╳╳╳│",
        "│╳╳╳╳╳╳╳╳╳│",
        "│╳╳╳╳╳╳╳╳╳│",
        "│╳╳╳╳╳╳╳╳╳│",
        "╰─────────╯",
    ]


def render_hand(hand: Hand | None, *, hidden: bool = False) -> Text:
    """Render a hand as Rich ``Text`` with five cards side by side."""
    text = Text()
    if hand is None:
        return Text("(sin cartas)")
    cards_lines: list[list[str]] = [
        _back_lines() if hidden else _card_lines(card) for card in hand.cards
    ]
    for row_index in range(_CARD_HEIGHT):
        for card_index, lines in enumerate(cards_lines):
            line = lines[row_index]
            color = "card_red" if (not hidden and hand.cards[card_index].suit.is_red) else "ink"
            text.append(line, style=color)
            if card_index < len(cards_lines) - 1:
                text.append("  ")
        text.append("\n")
    return text


def _console() -> Console:
    """Build a Rich console with no auto-highlighting (we style inline)."""
    return Console(highlight=False)


def _render_event(console: Console, event: DemoEvent) -> None:
    snap = event.snapshot
    console.rule(f"[bold #E8C547]{event.label}[/]")
    if snap.cpu_hand is not None:
        console.print("[#3E5147]CPU[/]")
        console.print(render_hand(snap.cpu_hand, hidden=not snap.cpu_hand_revealed))
    console.print(
        f"[#3E5147]bote:[/] [#E8C547]${int(snap.pot.amount)}[/]   "
        f"[#3E5147]apuesta:[/] [#C9D7CC]${int(snap.round_state.current_bet)}[/]"
    )
    if snap.human_hand is not None:
        console.print("[#3E5147]jugador[/]")
        console.print(render_hand(snap.human_hand))
    if snap.events:
        recent = "\n".join(f" · {e.detail}" for e in snap.events[-4:])
        console.print(Panel(recent, border_style="#3E5147", expand=False))


def run_text_demo(seed: int, *, interactive: bool = False) -> None:
    """Play a deterministic demo game and print it to the console.

    Args:
        seed: RNG seed.
        interactive: ignored in v1.0 — reserved for the CLI fallback.
            The demo is the same in both modes; the flag exists so the
            ``--no-tui`` path is documented and can diverge in v1.1.
    """
    _ = interactive  # explicit silence
    console = Console(highlight=False)
    rng = SeededRng(seed)
    session = GameSession(rng=rng)
    console.rule("[bold #5FB85F]PUNTO 81[/] · demo determinista")
    console.print(
        f"[#3E5147]seed:[/] [#E8C547]{seed}[/]   "
        f"[#3E5147]stack inicial:[/] [#C9D7CC]${int(session.snapshot.human.amount)}[/]"
    )
    events = play_demo_game(session, max_hands=6)
    for event in events:
        _render_event(console, event)
    final = session.snapshot
    console.rule("[bold #5FB85F]final[/]")
    console.print(
        f"jugador: [#E8C547]${int(final.human.amount)}[/]   "
        f"CPU: [#E8C547]${int(final.cpu.amount)}[/]"
    )
    last_phase: GamePhase = final.hand.phase
    if last_phase is GamePhase.GAME_OVER:
        if final.human.is_busted:
            console.print("[#D9534F]la CPU se lleva la partida[/]")
        else:
            console.print("[#7DDE7C]¡ganas la partida![/]")
    else:
        console.print("[#C9D7CC]demo completada sin nadie en quiebra[/]")


def render_snapshot(snapshot: HandSnapshot) -> Text:
    """Render a single snapshot (used by Textual widgets)."""
    text = Text()
    text.append("CPU\n", style="#3E5147")
    text.append(render_hand(snapshot.cpu_hand, hidden=not snapshot.cpu_hand_revealed))
    text.append(
        f"\nbote ${int(snapshot.pot.amount)}   apuesta ${int(snapshot.round_state.current_bet)}\n",
        style="#E8C547",
    )
    text.append("jugador\n", style="#3E5147")
    text.append(render_hand(snapshot.human_hand))
    return text
