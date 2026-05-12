"""``GameSession`` orchestrates whole games of 5-card draw.

The session is the public surface the presentation layer talks to.
Each call is one of the use cases of the application; they all return
immutable snapshots so the UI can render them without surprise.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum

from punto81.domain.models.deck import Deck
from punto81.domain.models.hand import Hand
from punto81.domain.models.money import (
    Bankroll,
    Chips,
    Pot,
    chips,
)
from punto81.domain.policies.cpu import (
    CpuActionKind,
    CpuResponse,
    choose_discards,
    open_bet,
    respond_to_bet,
)
from punto81.domain.ports.rng import Rng
from punto81.domain.rules.betting import (
    BetAction,
    BetActionKind,
    RoundState,
    apply_action,
)
from punto81.domain.rules.hand_evaluator import Evaluation
from punto81.domain.rules.showdown import Winner, resolve

ANTE: Chips = chips(5)
STARTING_STACK: Chips = chips(200)


class GamePhase(Enum):
    """Where in the hand lifecycle we currently are."""

    AWAITING_HAND = "awaiting_hand"
    FIRST_BET_HUMAN = "first_bet_human"
    DRAW_HUMAN = "draw_human"
    SECOND_BET_HUMAN = "second_bet_human"
    SHOWDOWN = "showdown"
    HAND_OVER = "hand_over"
    GAME_OVER = "game_over"


class GameSessionError(RuntimeError):
    """Raised when a transition is attempted in the wrong phase."""


@dataclass(frozen=True, slots=True)
class HandEvent:
    """A single thing that happened during a hand, for the UI log."""

    kind: str
    detail: str


@dataclass(frozen=True, slots=True)
class HandSnapshot:
    """All information about a hand in progress (or just finished)."""

    phase: GamePhase
    human_hand: Hand | None
    cpu_hand: Hand | None
    pot: Pot
    round_state: RoundState
    history: tuple[BetAction, ...] = ()
    events: tuple[HandEvent, ...] = ()
    winner: Winner | None = None
    human_eval: Evaluation | None = None
    cpu_eval: Evaluation | None = None
    cpu_hand_revealed: bool = False


@dataclass(frozen=True, slots=True)
class GameSnapshot:
    """The outward-facing view of the session after a transition."""

    human: Bankroll
    cpu: Bankroll
    hand: HandSnapshot
    schema_version: int = 1


def _initial_hand() -> HandSnapshot:
    return HandSnapshot(
        phase=GamePhase.AWAITING_HAND,
        human_hand=None,
        cpu_hand=None,
        pot=Pot(),
        round_state=RoundState(
            human=Bankroll(STARTING_STACK),
            cpu=Bankroll(STARTING_STACK),
            pot=Pot(),
        ),
    )


@dataclass(slots=True)
class GameSession:
    """High-level orchestrator for whole games.

    The session is mutable on purpose: presentation calls methods on it
    and reads ``snapshot`` afterwards. Each method runs a pure transition
    internally and replaces the snapshot.

    Attributes:
        rng: the random source. Inject ``SeededRng(seed)`` for
            reproducible games and ``SystemRng()`` otherwise.
    """

    rng: Rng
    _human: Bankroll = field(default_factory=lambda: Bankroll(STARTING_STACK))
    _cpu: Bankroll = field(default_factory=lambda: Bankroll(STARTING_STACK))
    _hand: HandSnapshot = field(default_factory=_initial_hand)
    _deck: Deck | None = None
    _history: list[BetAction] = field(default_factory=list)
    _events: list[HandEvent] = field(default_factory=list)

    @property
    def snapshot(self) -> GameSnapshot:
        """Return the current outward-facing snapshot."""
        return GameSnapshot(human=self._human, cpu=self._cpu, hand=self._hand)

    @classmethod
    def restore(cls, snapshot: GameSnapshot, rng: Rng) -> GameSession:
        """Rebuild a session from a persisted snapshot.

        The mid-hand deck is not persisted; if the snapshot is taken
        mid-hand the session resumes by discarding the hand and starting
        a fresh one (documented limitation v1.0).
        """
        return cls(
            rng=rng,
            _human=snapshot.human,
            _cpu=snapshot.cpu,
            _hand=_initial_hand(),
        )

    def start_hand(self) -> HandSnapshot:
        """Deal a new hand: collect antes, shuffle, deal 5/5, open bet by CPU.

        Returns:
            The new ``HandSnapshot`` after the CPU has opened.

        Raises:
            GameSessionError: if a hand is already underway, or if the
                game is over because someone busted.
        """
        if self._hand.phase not in {GamePhase.AWAITING_HAND, GamePhase.HAND_OVER}:
            raise GameSessionError(f"cannot start hand in phase {self._hand.phase}")
        if self._human.is_busted or self._cpu.is_busted:
            self._hand = replace(self._hand, phase=GamePhase.GAME_OVER)
            return self._hand

        human_after_ante = self._human.debit(ANTE) if self._human.can_afford(ANTE) else self._human
        cpu_after_ante = self._cpu.debit(ANTE) if self._cpu.can_afford(ANTE) else self._cpu
        pot_amount = chips(int(ANTE) * 2)
        pot = Pot(pot_amount)
        self._human = human_after_ante
        self._cpu = cpu_after_ante

        deck = Deck.shuffled(self.rng)
        deck, cpu_cards = deck.draw(5)
        deck, human_cards = deck.draw(5)
        self._deck = deck

        cpu_hand = Hand.of(cpu_cards)
        human_hand = Hand.of(human_cards)

        round_state = RoundState(human=self._human, cpu=self._cpu, pot=pot)
        opening = open_bet(cpu_hand, chips(int(self._cpu.amount)), self.rng)
        if opening > 0:
            round_state = apply_action(round_state, "cpu", BetAction(BetActionKind.BET, opening))
            self._cpu = round_state.cpu
            self._history = [BetAction(BetActionKind.BET, opening)]
            self._events = [
                HandEvent("deal", "ante de $5; reparto 5 cartas a cada jugador"),
                HandEvent("cpu_open", f"la CPU abre con ${int(opening)}"),
            ]
        else:
            round_state = apply_action(round_state, "cpu", BetAction(BetActionKind.CHECK))
            self._history = [BetAction(BetActionKind.CHECK)]
            self._events = [
                HandEvent("deal", "ante de $5; reparto 5 cartas a cada jugador"),
                HandEvent("cpu_check", "la CPU pasa"),
            ]

        self._hand = HandSnapshot(
            phase=GamePhase.FIRST_BET_HUMAN,
            human_hand=human_hand,
            cpu_hand=cpu_hand,
            pot=round_state.pot,
            round_state=round_state,
            history=tuple(self._history),
            events=tuple(self._events),
        )
        return self._hand

    def human_first_bet(self, action: BetAction) -> HandSnapshot:
        """Apply the human's response to the CPU's opening bet."""
        if self._hand.phase is not GamePhase.FIRST_BET_HUMAN:
            raise GameSessionError(f"cannot bet in phase {self._hand.phase}")

        round_state = apply_action(self._hand.round_state, "human", action)
        self._human = round_state.human
        self._history.append(action)
        self._events.append(_event_for_player_action(action, "humano"))

        if round_state.folded == "human":
            return self._finish_by_fold(round_state, winner=Winner.CPU)

        if action.kind is BetActionKind.RAISE:
            cpu_hand = self._hand.cpu_hand
            assert cpu_hand is not None
            response = respond_to_bet(
                cpu_hand,
                chips(int(round_state.current_bet) - int(round_state.cpu_committed)),
                chips(int(self._cpu.amount)),
                chips(int(round_state.pot.amount)),
                self.rng,
            )
            round_state = self._apply_cpu_response(round_state, response)
            if round_state.folded == "cpu":
                return self._finish_by_fold(round_state, winner=Winner.HUMAN)

        self._hand = replace(
            self._hand,
            phase=GamePhase.DRAW_HUMAN,
            pot=round_state.pot,
            round_state=round_state,
            history=tuple(self._history),
            events=tuple(self._events),
        )
        return self._hand

    def human_discard(self, positions: tuple[int, ...]) -> HandSnapshot:
        """Replace the human's chosen cards and run the CPU's draw."""
        if self._hand.phase is not GamePhase.DRAW_HUMAN:
            raise GameSessionError(f"cannot draw in phase {self._hand.phase}")
        if len(positions) > 3:
            raise GameSessionError("cannot discard more than 3 cards")
        assert self._deck is not None
        assert self._hand.human_hand is not None
        assert self._hand.cpu_hand is not None

        deck, new_human_cards = self._deck.draw(len(positions))
        human_hand = self._hand.human_hand.replace(positions, new_human_cards)
        self._events.append(
            HandEvent(
                "human_draw",
                f"el jugador descarta {len(positions)} carta(s)",
            )
        )

        cpu_discards = choose_discards(self._hand.cpu_hand)
        deck, new_cpu_cards = deck.draw(len(cpu_discards))
        cpu_hand = self._hand.cpu_hand.replace(cpu_discards, new_cpu_cards)
        self._events.append(HandEvent("cpu_draw", f"la CPU descarta {len(cpu_discards)} carta(s)"))

        self._deck = deck

        round_state = RoundState(
            human=self._human,
            cpu=self._cpu,
            pot=self._hand.pot,
        )
        self._history = []
        self._hand = replace(
            self._hand,
            phase=GamePhase.SECOND_BET_HUMAN,
            human_hand=human_hand,
            cpu_hand=cpu_hand,
            round_state=round_state,
            history=(),
            events=tuple(self._events),
        )
        return self._hand

    def human_second_bet(self, action: BetAction) -> HandSnapshot:
        """Apply the human's opening of the second betting round."""
        if self._hand.phase is not GamePhase.SECOND_BET_HUMAN:
            raise GameSessionError(f"cannot bet in phase {self._hand.phase}")

        round_state = apply_action(self._hand.round_state, "human", action)
        self._human = round_state.human
        self._history.append(action)
        self._events.append(_event_for_player_action(action, "humano"))

        if round_state.folded == "human":
            return self._finish_by_fold(round_state, winner=Winner.CPU)

        # CPU now responds to whatever the human did.
        cpu_hand = self._hand.cpu_hand
        assert cpu_hand is not None
        to_call = chips(int(round_state.current_bet) - int(round_state.cpu_committed))
        if to_call == 0 and action.kind is BetActionKind.CHECK:
            cpu_response_action = BetAction(BetActionKind.CHECK)
            round_state = apply_action(round_state, "cpu", cpu_response_action)
            self._history.append(cpu_response_action)
            self._events.append(HandEvent("cpu_check", "la CPU pasa"))
        else:
            response = respond_to_bet(
                cpu_hand,
                to_call,
                chips(int(self._cpu.amount)),
                chips(int(round_state.pot.amount)),
                self.rng,
            )
            round_state = self._apply_cpu_response(round_state, response)
            if round_state.folded == "cpu":
                return self._finish_by_fold(round_state, winner=Winner.HUMAN)

        # If the CPU raised, the human must call or fold to close — we
        # auto-call here to keep v1.0 simple (documented limitation).
        if round_state.human_committed < round_state.current_bet:
            call_action = BetAction(BetActionKind.CALL)
            round_state = apply_action(round_state, "human", call_action)
            self._human = round_state.human
            self._history.append(call_action)
            self._events.append(HandEvent("human_call", "el jugador iguala la subida"))

        return self._finalize_showdown(round_state)

    def _apply_cpu_response(self, state: RoundState, response: CpuResponse) -> RoundState:
        if response.kind is CpuActionKind.FOLD:
            updated = apply_action(state, "cpu", BetAction(BetActionKind.FOLD))
            self._history.append(BetAction(BetActionKind.FOLD))
            self._events.append(HandEvent("cpu_fold", "la CPU se retira"))
            return updated
        if response.kind is CpuActionKind.CALL:
            updated = apply_action(state, "cpu", BetAction(BetActionKind.CALL))
            self._cpu = updated.cpu
            self._history.append(BetAction(BetActionKind.CALL))
            self._events.append(HandEvent("cpu_call", "la CPU iguala"))
            return updated
        raise_action = BetAction(BetActionKind.RAISE, response.raise_amount)
        updated = apply_action(state, "cpu", raise_action)
        self._cpu = updated.cpu
        self._history.append(raise_action)
        self._events.append(
            HandEvent(
                "cpu_raise",
                f"la CPU iguala y sube ${int(response.raise_amount)}",
            )
        )
        return updated

    def _finish_by_fold(self, round_state: RoundState, winner: Winner) -> HandSnapshot:
        empty_pot, taken = round_state.pot.take_all()
        if winner is Winner.HUMAN:
            self._human = self._human.credit(taken)
            self._events.append(HandEvent("human_wins", f"el jugador se lleva ${int(taken)}"))
        else:
            self._cpu = self._cpu.credit(taken)
            self._events.append(HandEvent("cpu_wins", f"la CPU se lleva ${int(taken)}"))
        next_phase = (
            GamePhase.GAME_OVER
            if self._human.is_busted or self._cpu.is_busted
            else GamePhase.HAND_OVER
        )
        self._hand = replace(
            self._hand,
            phase=next_phase,
            pot=empty_pot,
            round_state=replace(round_state, pot=empty_pot),
            winner=winner,
            history=tuple(self._history),
            events=tuple(self._events),
        )
        return self._hand

    def _finalize_showdown(self, round_state: RoundState) -> HandSnapshot:
        human_hand = self._hand.human_hand
        cpu_hand = self._hand.cpu_hand
        assert human_hand is not None
        assert cpu_hand is not None
        result = resolve(human_hand, cpu_hand)
        empty_pot, taken = round_state.pot.take_all()

        if result.winner is Winner.HUMAN:
            self._human = self._human.credit(taken)
            self._events.append(
                HandEvent(
                    "human_wins",
                    f"el jugador gana con {result.human_eval.label_es} (${int(taken)})",
                )
            )
        elif result.winner is Winner.CPU:
            self._cpu = self._cpu.credit(taken)
            self._events.append(
                HandEvent(
                    "cpu_wins",
                    f"la CPU gana con {result.cpu_eval.label_es} (${int(taken)})",
                )
            )
        else:
            _, first, second = Pot(taken).split()
            self._human = self._human.credit(first)
            self._cpu = self._cpu.credit(second)
            self._events.append(HandEvent("tie", f"empate: el bote (${int(taken)}) se reparte"))

        next_phase = (
            GamePhase.GAME_OVER
            if self._human.is_busted or self._cpu.is_busted
            else GamePhase.HAND_OVER
        )

        self._hand = replace(
            self._hand,
            phase=next_phase,
            pot=empty_pot,
            round_state=replace(round_state, pot=empty_pot),
            winner=result.winner,
            human_eval=result.human_eval,
            cpu_eval=result.cpu_eval,
            cpu_hand_revealed=True,
            history=tuple(self._history),
            events=tuple(self._events),
        )
        return self._hand


def _event_for_player_action(action: BetAction, actor: str) -> HandEvent:
    match action.kind:
        case BetActionKind.CHECK:
            return HandEvent(f"{actor}_check", f"el {actor} pasa")
        case BetActionKind.FOLD:
            return HandEvent(f"{actor}_fold", f"el {actor} se retira")
        case BetActionKind.BET:
            return HandEvent(f"{actor}_bet", f"el {actor} apuesta ${int(action.amount)}")
        case BetActionKind.CALL:
            return HandEvent(f"{actor}_call", f"el {actor} iguala")
        case BetActionKind.RAISE:
            return HandEvent(
                f"{actor}_raise",
                f"el {actor} sube ${int(action.amount)}",
            )


__all__ = [
    "ANTE",
    "STARTING_STACK",
    "GamePhase",
    "GameSession",
    "GameSessionError",
    "GameSnapshot",
    "HandEvent",
    "HandSnapshot",
]
