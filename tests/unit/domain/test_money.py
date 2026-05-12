"""Tests for chip primitives."""

from __future__ import annotations

import pytest

from punto81.domain.models.money import (
    Bankroll,
    InsufficientFundsError,
    Pot,
    chips,
)


def test_chips_rejects_negative() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        chips(-1)


def test_bankroll_debit_and_credit() -> None:
    bankroll = Bankroll(amount=chips(100))
    after_bet = bankroll.debit(chips(40))
    assert after_bet.amount == 60
    refilled = after_bet.credit(chips(10))
    assert refilled.amount == 70


def test_bankroll_busted_when_zero() -> None:
    bankroll = Bankroll(amount=chips(0))
    assert bankroll.is_busted is True


def test_bankroll_debit_raises_when_insufficient() -> None:
    bankroll = Bankroll(amount=chips(5))
    with pytest.raises(InsufficientFundsError):
        bankroll.debit(chips(10))


def test_pot_add_and_take_all() -> None:
    pot = Pot().add(chips(50)).add(chips(30))
    assert pot.amount == 80
    empty, taken = pot.take_all()
    assert empty.amount == 0
    assert taken == 80


def test_pot_split_awards_odd_chip_to_first() -> None:
    pot = Pot(amount=chips(11))
    empty, first, second = pot.split()
    assert empty.amount == 0
    assert first == 6
    assert second == 5
