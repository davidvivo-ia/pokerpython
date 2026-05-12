"""Tests for the persistence adapters."""

from __future__ import annotations

from pathlib import Path

from punto81.application.use_cases.game_session import GameSession
from punto81.domain.ports.rng import Rng
from punto81.infrastructure.persistence.in_memory import InMemorySaveStore
from punto81.infrastructure.persistence.json_save_store import (
    JsonSaveStore,
    default_save_path,
)


def test_in_memory_round_trip(rng: Rng) -> None:
    session = GameSession(rng=rng)
    store = InMemorySaveStore()
    store.save(session.snapshot)
    loaded = store.load()
    assert loaded is not None
    assert loaded.human.amount == session.snapshot.human.amount


def test_in_memory_clear(rng: Rng) -> None:
    session = GameSession(rng=rng)
    store = InMemorySaveStore()
    store.save(session.snapshot)
    store.clear()
    assert store.load() is None


def test_json_round_trip(tmp_path: Path, rng: Rng) -> None:
    path = tmp_path / "save.json"
    store = JsonSaveStore(path=path)
    session = GameSession(rng=rng)
    session.start_hand()
    store.save(session.snapshot)
    loaded = store.load()
    assert loaded is not None
    assert loaded.human.amount == session.snapshot.human.amount
    assert loaded.cpu.amount == session.snapshot.cpu.amount


def test_json_missing_returns_none(tmp_path: Path) -> None:
    store = JsonSaveStore(path=tmp_path / "absent.json")
    assert store.load() is None


def test_json_corrupt_returns_none(tmp_path: Path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not valid json", encoding="utf-8")
    store = JsonSaveStore(path=path)
    assert store.load() is None


def test_json_clear_removes_file(tmp_path: Path, rng: Rng) -> None:
    path = tmp_path / "save.json"
    store = JsonSaveStore(path=path)
    store.save(GameSession(rng=rng).snapshot)
    assert path.exists()
    store.clear()
    assert not path.exists()
    # clear is idempotent
    store.clear()


def test_default_save_path_under_xdg() -> None:
    p = default_save_path()
    assert p.name == "save.json"
    assert "punto81" in str(p)
