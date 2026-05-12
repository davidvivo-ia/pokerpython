"""Tests for the RNG adapters."""

from __future__ import annotations

from punto81.domain.ports.rng import Rng
from punto81.infrastructure.rng.seeded import SeededRng
from punto81.infrastructure.rng.system import SystemRng


def test_seeded_rng_is_reproducible() -> None:
    a = SeededRng(42)
    b = SeededRng(42)
    assert a.randint(0, 100) == b.randint(0, 100)
    assert a.shuffle_indices(52) == b.shuffle_indices(52)


def test_seeded_rng_returns_float_in_range() -> None:
    rng = SeededRng(7)
    value = rng.random()
    assert 0.0 <= value < 1.0


def test_seeded_rng_shuffle_is_permutation() -> None:
    rng = SeededRng(123)
    indices = rng.shuffle_indices(52)
    assert sorted(indices) == list(range(52))


def test_system_rng_satisfies_protocol() -> None:
    rng: Rng = SystemRng()
    assert rng.randint(1, 5) in {1, 2, 3, 4, 5}
    assert 0.0 <= rng.random() < 1.0
    assert sorted(rng.shuffle_indices(10)) == list(range(10))
