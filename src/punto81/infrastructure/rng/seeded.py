"""Seeded RNG adapter built on ``random.Random``."""

from __future__ import annotations

import random
from dataclasses import dataclass, field


@dataclass(slots=True)
class SeededRng:
    """Deterministic RNG seeded from ``seed``.

    Same seed always produces the same sequence of randoms, which is the
    contract behind ``--seed`` and ``--demo``.
    """

    seed: int
    _random: random.Random = field(init=False)

    def __post_init__(self) -> None:
        self._random = random.Random(self.seed)

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
