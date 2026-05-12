"""Money primitives: chip amounts, player bankrolls and the pot."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Final, NewType

Chips = NewType("Chips", int)

ZERO_CHIPS: Final[Chips] = Chips(0)


class InsufficientFundsError(ValueError):
    """A player cannot afford the requested wager."""


def chips(amount: int) -> Chips:
    """Build a ``Chips`` value with sign validation.

    Args:
        amount: non-negative integer chip count.

    Returns:
        A ``Chips`` value.

    Raises:
        ValueError: if ``amount`` is negative.
    """
    if amount < 0:
        raise ValueError(f"chip amount must be non-negative, got {amount}")
    return Chips(amount)


@dataclass(frozen=True, slots=True)
class Bankroll:
    """How many chips a player owns at this moment."""

    amount: Chips

    def can_afford(self, wager: Chips) -> bool:
        """Return whether the player has at least ``wager`` chips."""
        return self.amount >= wager

    def debit(self, wager: Chips) -> Bankroll:
        """Return a new bankroll with ``wager`` chips removed.

        Raises:
            InsufficientFundsError: if the wager exceeds the balance.
        """
        if not self.can_afford(wager):
            raise InsufficientFundsError(f"cannot debit {wager} from bankroll of {self.amount}")
        return replace(self, amount=Chips(self.amount - wager))

    def credit(self, gain: Chips) -> Bankroll:
        """Return a new bankroll with ``gain`` chips added."""
        return replace(self, amount=Chips(self.amount + gain))

    @property
    def is_busted(self) -> bool:
        """Whether the player has zero chips left."""
        return self.amount == 0


@dataclass(frozen=True, slots=True)
class Pot:
    """Chips currently at stake in the running hand."""

    amount: Chips = ZERO_CHIPS

    def add(self, contribution: Chips) -> Pot:
        """Return a new pot with ``contribution`` added."""
        return replace(self, amount=Chips(self.amount + contribution))

    def take_all(self) -> tuple[Pot, Chips]:
        """Collect the entire pot.

        Returns:
            A pair ``(empty_pot, taken_chips)``.
        """
        return Pot(ZERO_CHIPS), self.amount

    def split(self) -> tuple[Pot, Chips, Chips]:
        """Split the pot in half, awarding any odd chip to the first slot.

        Returns:
            A triple ``(empty_pot, first_half, second_half)``.
        """
        first = (self.amount + 1) // 2
        second = self.amount // 2
        return Pot(ZERO_CHIPS), Chips(first), Chips(second)
