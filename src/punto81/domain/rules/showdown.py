"""Showdown resolution: compare two hands and decide who takes the pot."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from punto81.domain.models.hand import Hand
from punto81.domain.rules.hand_evaluator import Evaluation, evaluate


class Winner(Enum):
    """Outcome of a showdown."""

    HUMAN = "human"
    CPU = "cpu"
    TIE = "tie"


@dataclass(frozen=True, slots=True)
class ShowdownResult:
    """Outcome plus both evaluations for display purposes."""

    winner: Winner
    human_eval: Evaluation
    cpu_eval: Evaluation


def resolve(human: Hand, cpu: Hand) -> ShowdownResult:
    """Compare two hands and return a ``ShowdownResult``.

    Args:
        human: the human player's hand.
        cpu: the CPU's hand.

    Returns:
        A ``ShowdownResult`` describing the winner and both evaluations.
    """
    human_eval = evaluate(human)
    cpu_eval = evaluate(cpu)
    if human_eval > cpu_eval:
        winner = Winner.HUMAN
    elif cpu_eval > human_eval:
        winner = Winner.CPU
    else:
        winner = Winner.TIE
    return ShowdownResult(winner=winner, human_eval=human_eval, cpu_eval=cpu_eval)
