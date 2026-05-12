"""Shared pytest fixtures and helpers."""

from __future__ import annotations

import random

import pytest

from punto81.domain.ports.rng import Rng


class _DeterministicRng:
    """In-memory seeded RNG used across tests (avoids importing infra here)."""

    def __init__(self, seed: int) -> None:
        self._random = random.Random(seed)

    def randint(self, low: int, high: int) -> int:
        return self._random.randint(low, high)

    def random(self) -> float:
        return self._random.random()

    def shuffle_indices(self, n: int) -> tuple[int, ...]:
        indices = list(range(n))
        self._random.shuffle(indices)
        return tuple(indices)


@pytest.fixture
def rng() -> Rng:
    """Return a deterministic RNG seeded with 42 for reproducible tests."""
    return _DeterministicRng(42)
