"""In-memory save store for tests and `--demo`."""

from __future__ import annotations

from dataclasses import dataclass

from punto81.application.use_cases.game_session import GameSnapshot


@dataclass(slots=True)
class InMemorySaveStore:
    """Save store that only remembers the last snapshot in process memory."""

    _snapshot: GameSnapshot | None = None

    def save(self, snapshot: GameSnapshot) -> None:
        """Remember ``snapshot``."""
        self._snapshot = snapshot

    def load(self) -> GameSnapshot | None:
        """Return the latest remembered snapshot."""
        return self._snapshot

    def clear(self) -> None:
        """Forget the snapshot."""
        self._snapshot = None
