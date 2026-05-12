"""System RNG adapter built on ``random.SystemRandom``."""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass(slots=True)
class SystemRng:
    """Non-deterministic RNG backed by ``random.SystemRandom``."""

    _random: random.SystemRandom = field(default_factory=random.SystemRandom)

    def randint(self, low: int, high: int) -> int:
        """Return an integer in ``[low, high]``."""
        return self._random.randint(low, high)

    def random(self) -> float:
        """Return a float in ``[0.0, 1.0)``."""
        return self._random.random()

    def shuffle_indices(self, n: int) -> tuple[int, ...]:
        """Return a shuffled permutation of ``range(n)``."""
        indices = list(range(n))
        self._random.shuffle(indices)
        return tuple(indices)
