"""System clock adapter (placeholder for v1.0)."""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass(slots=True)
class SystemClock:
    """Wall-clock adapter."""

    def now(self) -> float:
        """Return seconds since the epoch."""
        return time.time()
