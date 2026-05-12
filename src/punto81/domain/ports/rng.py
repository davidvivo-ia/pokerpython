"""Random number generator port.

The domain only depends on this Protocol. Concrete implementations live
in ``infrastructure.rng``.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class Rng(Protocol):
    """Minimal random source the domain needs.

    Implementations must be deterministic for a given construction seed
    so that ``--seed`` and ``--demo`` modes remain reproducible.
    """

    def randint(self, low: int, high: int) -> int:
        """Return an integer ``N`` such that ``low <= N <= high``."""

    def random(self) -> float:
        """Return a float in the half-open interval ``[0.0, 1.0)``."""

    def shuffle_indices(self, n: int) -> tuple[int, ...]:
        """Return a permutation of ``range(n)`` as an immutable tuple."""
