"""Typer CLI definition (scaffold; logic lands in Phase 7)."""

from __future__ import annotations

import typer

app: typer.Typer = typer.Typer(
    name="punto81",
    help="Punto 81 — 5-card draw poker in your terminal.",
    no_args_is_help=False,
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def main() -> None:
    """Bootstrap entry point — implementation arrives in Phase 7."""
    typer.echo("punto81 scaffold ready — TUI not implemented yet.")
