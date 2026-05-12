"""Persistence port: stores and loads ``GameSnapshot`` objects."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from punto81.application.use_cases.game_session import GameSnapshot


@runtime_checkable
class SaveStore(Protocol):
    """Abstraction over how a save game is persisted."""

    def save(self, snapshot: GameSnapshot) -> None:
        """Persist ``snapshot`` so a later ``load`` can return it."""

    def load(self) -> GameSnapshot | None:
        """Return the most recent snapshot, or ``None`` if there is none."""

    def clear(self) -> None:
        """Remove any saved snapshot (used after game over)."""
