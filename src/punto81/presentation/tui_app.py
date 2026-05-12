"""Textual TUI application — single-screen 5-card draw vs CPU."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, Label, Log, Static

from punto81 import __version__
from punto81.application.use_cases.game_session import (
    GamePhase,
    GameSession,
    HandSnapshot,
)
from punto81.domain.models.hand import Hand
from punto81.domain.models.money import chips
from punto81.domain.ports.rng import Rng
from punto81.domain.rules.betting import BetAction, BetActionKind
from punto81.domain.rules.showdown import Winner
from punto81.infrastructure.rng.seeded import SeededRng
from punto81.infrastructure.rng.system import SystemRng
from punto81.presentation.widgets.card_widget import CardWidget

ASSETS_DIR: Path = Path(__file__).parent.parent / "assets"


class HandRow(Horizontal):
    """A horizontal row of five card widgets."""

    DEFAULT_CSS = """
    HandRow {
        height: 9;
        content-align: center middle;
        align: center middle;
    }
    """

    def __init__(self, *, hidden: bool, identifier: str) -> None:
        super().__init__(id=identifier)
        self._hidden = hidden
        self._card_widgets: list[CardWidget] = []

    def compose(self) -> ComposeResult:
        for _ in range(5):
            widget = CardWidget(hidden=self._hidden)
            self._card_widgets.append(widget)
            yield widget

    def update_hand(self, hand: Hand | None, *, hidden: bool = False) -> None:
        """Refresh the five cards from a domain ``Hand`` (or hide them)."""
        if hand is None:
            for widget in self._card_widgets:
                widget.update_card(None, hidden=True)
            return
        for widget, card in zip(self._card_widgets, hand.cards, strict=True):
            widget.update_card(card, hidden=hidden)


class Punto81App(App[None]):
    """Main Textual application."""

    CSS_PATH = str(ASSETS_DIR / "tcss" / "app.tcss")
    TITLE = "PUNTO 81"
    SUB_TITLE = f"5-card draw  ·  v{__version__}"

    BINDINGS: ClassVar[list[Binding | tuple[str, str] | tuple[str, str, str]]] = [
        Binding("q", "quit", "Salir"),
        Binding("?", "help", "Ayuda"),
        Binding("enter", "advance", "Continuar", priority=True),
        Binding("c", "check", "Pasar"),
        Binding("f", "fold", "Retirarse"),
        Binding("b", "bet", "Apostar"),
        Binding("r", "raise_bet", "Subir"),
        Binding("d", "deal", "Repartir"),
        Binding("space", "draw", "Descartar"),
        Binding("1", "toggle_1", "1"),
        Binding("2", "toggle_2", "2"),
        Binding("3", "toggle_3", "3"),
        Binding("4", "toggle_4", "4"),
        Binding("5", "toggle_5", "5"),
    ]

    def __init__(self, *, seed: int | None = None, animations: bool = True) -> None:
        super().__init__()
        rng: Rng = SeededRng(seed) if seed is not None else SystemRng()
        self.session = GameSession(rng=rng)
        self._selected: set[int] = set()
        self._animations = animations

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        with Vertical(id="root"):
            yield Label("CPU", classes="label")
            yield HandRow(hidden=True, identifier="cpu-hand")
            yield Static("$0", id="pot")
            yield Label("jugador", classes="label")
            yield HandRow(hidden=False, identifier="human-hand")
            yield Static("Pulsa [d] para repartir una mano.", id="status")
            yield Log(highlight=False, id="event-log", classes="event-log")
            yield Static("", id="prompt")
            yield Input(
                placeholder="cantidad (Enter para confirmar)",
                id="amount-input",
            )
        yield Footer()

    def on_mount(self) -> None:
        amount_input = self.query_one("#amount-input", Input)
        amount_input.display = False
        self._refresh()

    def _refresh(self) -> None:
        snap = self.session.snapshot
        self.query_one("#cpu-hand", HandRow).update_hand(
            snap.hand.cpu_hand, hidden=not snap.hand.cpu_hand_revealed
        )
        self.query_one("#human-hand", HandRow).update_hand(snap.hand.human_hand)
        self.query_one("#pot", Static).update(
            f"bote  ${int(snap.hand.pot.amount)}    "
            f"apuesta  ${int(snap.hand.round_state.current_bet)}    "
            f"·    jugador ${int(snap.human.amount)}    CPU ${int(snap.cpu.amount)}"
        )
        self.query_one("#status", Static).update(_status_text(snap.hand))
        log = self.query_one("#event-log", Log)
        log.clear()
        for event in snap.hand.events[-6:]:
            log.write_line(f"· {event.detail}")
        self.query_one("#prompt", Static).update(_prompt_text(snap.hand, self._selected))

    # -- key actions ---------------------------------------------------

    def action_help(self) -> None:
        log = self.query_one("#event-log", Log)
        log.write_line(
            "[d] repartir  ·  [c] pasar  ·  [b] apostar  ·  [r] subir  ·  "
            "[f] retirarse  ·  [1-5] toggle descarte  ·  [space] confirmar descarte"
        )

    def action_deal(self) -> None:
        if self.session.snapshot.hand.phase in {
            GamePhase.AWAITING_HAND,
            GamePhase.HAND_OVER,
        }:
            self.session.start_hand()
            self._selected.clear()
            self._refresh()

    def action_check(self) -> None:
        phase = self.session.snapshot.hand.phase
        if phase is GamePhase.FIRST_BET_HUMAN:
            self._safe_action(lambda: self.session.human_first_bet(BetAction(BetActionKind.CHECK)))
        elif phase is GamePhase.SECOND_BET_HUMAN:
            self._safe_action(lambda: self.session.human_second_bet(BetAction(BetActionKind.CHECK)))

    def action_fold(self) -> None:
        phase = self.session.snapshot.hand.phase
        if phase is GamePhase.FIRST_BET_HUMAN:
            self._safe_action(lambda: self.session.human_first_bet(BetAction(BetActionKind.FOLD)))
        elif phase is GamePhase.SECOND_BET_HUMAN:
            self._safe_action(lambda: self.session.human_second_bet(BetAction(BetActionKind.FOLD)))

    def action_bet(self) -> None:
        phase = self.session.snapshot.hand.phase
        if phase is GamePhase.FIRST_BET_HUMAN:
            self._safe_action(lambda: self.session.human_first_bet(BetAction(BetActionKind.CALL)))
        elif phase is GamePhase.SECOND_BET_HUMAN:
            self._open_amount_prompt(BetActionKind.BET)

    def action_raise_bet(self) -> None:
        phase = self.session.snapshot.hand.phase
        if phase in {GamePhase.FIRST_BET_HUMAN, GamePhase.SECOND_BET_HUMAN}:
            self._open_amount_prompt(BetActionKind.RAISE)

    def action_advance(self) -> None:
        phase = self.session.snapshot.hand.phase
        if phase is GamePhase.HAND_OVER:
            self.action_deal()
        elif phase is GamePhase.GAME_OVER:
            self.exit(return_code=0)

    def action_draw(self) -> None:
        if self.session.snapshot.hand.phase is not GamePhase.DRAW_HUMAN:
            return
        positions = tuple(sorted(self._selected))
        try:
            self.session.human_discard(positions)
        except (ValueError, RuntimeError) as exc:  # pragma: no cover - UX guard
            self.query_one("#event-log", Log).write_line(f"⚠  {exc}")
        self._selected.clear()
        self._refresh()

    def action_toggle_1(self) -> None:
        self._toggle(0)

    def action_toggle_2(self) -> None:
        self._toggle(1)

    def action_toggle_3(self) -> None:
        self._toggle(2)

    def action_toggle_4(self) -> None:
        self._toggle(3)

    def action_toggle_5(self) -> None:
        self._toggle(4)

    def _toggle(self, index: int) -> None:
        if self.session.snapshot.hand.phase is not GamePhase.DRAW_HUMAN:
            return
        if index in self._selected:
            self._selected.remove(index)
        elif len(self._selected) < 3:
            self._selected.add(index)
        self._refresh()

    def _open_amount_prompt(self, kind: BetActionKind) -> None:
        amount_input = self.query_one("#amount-input", Input)
        amount_input.display = True
        amount_input.value = ""
        amount_input.placeholder = "cantidad a subir" if kind is BetActionKind.RAISE else "apuesta"
        amount_input.focus()
        self._pending_kind = kind

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Receive the wagered amount and apply the pending action."""
        amount_input = self.query_one("#amount-input", Input)
        amount_input.display = False
        try:
            value = int(event.value)
        except ValueError:
            self.query_one("#event-log", Log).write_line("⚠  cantidad inválida")
            return
        kind = getattr(self, "_pending_kind", BetActionKind.BET)
        action = BetAction(kind, chips(max(1, value)))
        phase = self.session.snapshot.hand.phase
        if phase is GamePhase.FIRST_BET_HUMAN:
            self._safe_action(lambda: self.session.human_first_bet(action))
        elif phase is GamePhase.SECOND_BET_HUMAN:
            self._safe_action(lambda: self.session.human_second_bet(action))

    def _safe_action(self, runner: object) -> None:
        try:
            assert callable(runner)
            runner()
        except (ValueError, RuntimeError) as exc:  # pragma: no cover - UX guard
            self.query_one("#event-log", Log).write_line(f"⚠  {exc}")
        self._refresh()


def _status_text(snapshot: HandSnapshot) -> str:
    match snapshot.phase:
        case GamePhase.AWAITING_HAND:
            return "Pulsa [d] para repartir una mano."
        case GamePhase.FIRST_BET_HUMAN:
            return "tu turno · [c] pasar  [b] igualar  [r] subir  [f] retirarse"
        case GamePhase.DRAW_HUMAN:
            return "descarte · [1-5] seleccionar  [space] confirmar"
        case GamePhase.SECOND_BET_HUMAN:
            return "tu turno · [c] pasar  [b] apostar  [r] subir  [f] retirarse"
        case GamePhase.HAND_OVER:
            winner = snapshot.winner
            if winner is Winner.HUMAN:
                return "ganas la mano · [Enter] otra"
            if winner is Winner.CPU:
                return "la CPU se lleva esta mano · [Enter] otra"
            return "empate · [Enter] otra"
        case GamePhase.GAME_OVER:
            return "fin de partida · [Enter] salir"
        case _:
            return ""


def _prompt_text(snapshot: HandSnapshot, selected: set[int]) -> str:
    if snapshot.phase is GamePhase.DRAW_HUMAN:
        selected_str = ", ".join(str(i + 1) for i in sorted(selected)) or "ninguna"
        return f"seleccionadas: {selected_str}"
    return ""


__all__ = ["Punto81App"]
