"""Smoke tests for the CLI."""

from __future__ import annotations

from typer.testing import CliRunner

from punto81.presentation.cli import app


def test_version_flag_prints_version() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "punto81" in result.stdout


def test_demo_flag_runs_to_completion() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--demo", "--seed", "42"])
    assert result.exit_code == 0
    assert "PUNTO 81" in result.stdout
    assert "final" in result.stdout


def test_demo_with_no_tui_runs_to_completion() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["--no-tui", "--seed", "1"])
    assert result.exit_code == 0
    assert "final" in result.stdout
