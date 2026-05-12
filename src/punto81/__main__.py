"""CLI entry point for the ``punto81`` command.

The Typer application is exposed as ``app`` so that ``[project.scripts]``
in ``pyproject.toml`` can dispatch ``punto81`` directly to it.
"""

from __future__ import annotations

from punto81.presentation.cli import app

__all__ = ["app"]


if __name__ == "__main__":  # pragma: no cover - manual entry
    app()
