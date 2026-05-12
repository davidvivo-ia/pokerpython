"""Smoke test that the package imports."""

from __future__ import annotations

import punto81


def test_package_version() -> None:
    assert punto81.__version__ == "1.0.0"
