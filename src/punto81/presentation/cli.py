"""Typer CLI: dispatches between TUI, headless demo and CLI fallback."""

from __future__ import annotations

import typer

from punto81 import __version__
from punto81.presentation.demo_runner import run_text_demo

app: typer.Typer = typer.Typer(
    name="punto81",
    help="Punto 81 — 5-card draw poker en tu terminal.",
    no_args_is_help=False,
    add_completion=False,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"punto81 {__version__}")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    seed: int | None = typer.Option(
        None,
        "--seed",
        help="Fija la semilla del RNG para partidas reproducibles.",
        show_default=False,
    ),
    demo: bool = typer.Option(
        False,
        "--demo",
        help="Reproduce una partida automática sin intervención humana.",
    ),
    no_tui: bool = typer.Option(
        False,
        "--no-tui",
        help="Fuerza salida en texto plano (sin Textual).",
    ),
    no_animations: bool = typer.Option(
        False,
        "--no-animations",
        help="Desactiva animaciones (accesibilidad / terminales lentos).",
    ),
    version: bool = typer.Option(
        False,
        "--version",
        callback=_version_callback,
        is_eager=True,
        help="Muestra la versión y sale.",
    ),
) -> None:
    """Punto entry point."""
    if ctx.invoked_subcommand is not None:
        return

    if demo:
        run_text_demo(seed=seed if seed is not None else 42)
        return

    if no_tui:
        run_text_demo(seed=seed if seed is not None else 42, interactive=True)
        return

    # Lazy import: Textual is heavy and not always desired.
    from punto81.presentation.tui_app import Punto81App  # noqa: PLC0415

    Punto81App(seed=seed, animations=not no_animations).run()
