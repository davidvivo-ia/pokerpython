"""JSON-on-disk save store using XDG locations and pydantic validation."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import structlog
from platformdirs import user_data_dir
from pydantic import BaseModel, Field, ValidationError

from punto81.application.use_cases.game_session import (
    GamePhase,
    GameSnapshot,
    HandSnapshot,
)
from punto81.domain.models.money import Bankroll, Pot, chips
from punto81.domain.rules.betting import RoundState

logger = structlog.get_logger(__name__)


class _PotModel(BaseModel):
    amount: int = Field(ge=0)


class _BankrollModel(BaseModel):
    amount: int = Field(ge=0)


class _SaveModel(BaseModel):
    """Pydantic model used to round-trip a ``GameSnapshot`` through JSON."""

    schema_version: int = 1
    human: _BankrollModel
    cpu: _BankrollModel
    pot: _PotModel
    phase: str


def _model_from_snapshot(snapshot: GameSnapshot) -> _SaveModel:
    return _SaveModel(
        schema_version=snapshot.schema_version,
        human=_BankrollModel(amount=int(snapshot.human.amount)),
        cpu=_BankrollModel(amount=int(snapshot.cpu.amount)),
        pot=_PotModel(amount=int(snapshot.hand.pot.amount)),
        phase=snapshot.hand.phase.value,
    )


def _snapshot_from_model(model: _SaveModel) -> GameSnapshot:
    bankroll_human = Bankroll(chips(model.human.amount))
    bankroll_cpu = Bankroll(chips(model.cpu.amount))
    pot = Pot(chips(model.pot.amount))
    hand = HandSnapshot(
        phase=GamePhase(model.phase),
        human_hand=None,
        cpu_hand=None,
        pot=pot,
        round_state=RoundState(human=bankroll_human, cpu=bankroll_cpu, pot=pot),
    )
    return GameSnapshot(
        human=bankroll_human,
        cpu=bankroll_cpu,
        hand=hand,
        schema_version=model.schema_version,
    )


def default_save_path() -> Path:
    """Return the XDG-aware default path for the save file."""
    base = Path(user_data_dir(appname="punto81", appauthor=False))
    return base / "save.json"


@dataclass(slots=True)
class JsonSaveStore:
    """Save game persistence using a single JSON file."""

    path: Path

    def save(self, snapshot: GameSnapshot) -> None:
        """Persist ``snapshot`` to disk, creating parents if needed."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        model = _model_from_snapshot(snapshot)
        self.path.write_text(model.model_dump_json(indent=2), encoding="utf-8")

    def load(self) -> GameSnapshot | None:
        """Return the most recent snapshot, or ``None`` if there is none."""
        if not self.path.exists():
            return None
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            model = _SaveModel.model_validate(raw)
        except (json.JSONDecodeError, ValidationError) as exc:
            logger.log(
                logging.WARNING,
                "save file is corrupt; starting fresh",
                path=str(self.path),
                error=str(exc),
            )
            return None
        return _snapshot_from_model(model)

    def clear(self) -> None:
        """Delete the save file if it exists."""
        self.path.unlink(missing_ok=True)
