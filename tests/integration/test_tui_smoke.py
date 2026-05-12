"""Headless smoke test that the Textual app boots."""

from __future__ import annotations

import pytest

from punto81.presentation.tui_app import Punto81App


@pytest.mark.asyncio
async def test_app_starts_and_deals() -> None:
    app = Punto81App(seed=42)
    async with app.run_test() as pilot:
        await pilot.press("d")  # deal a hand
        await pilot.pause()
        snap = app.session.snapshot
        assert snap.hand.human_hand is not None
        assert snap.hand.cpu_hand is not None
        await pilot.press("c")  # check / call the CPU's open
        await pilot.pause()
        await pilot.press("q")
