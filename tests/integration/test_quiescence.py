"""Test quiescence equivalence

I test different quiescence functions/parameters to test their equivalence.
"""

from collections import deque

import pytest

from herald import board, evaluation, move_ordering
from herald.quiescence import quiescence
from herald.configuration import Config
from herald.constants import VALUE_MAX
from herald.data_structures import to_uci

fens = []
with open("tests/epd/wac.epd", "r", encoding="utf-8") as wacfile:
    for line in wacfile:
        epd = line.split()
        fens.append(" ".join(epd[:4]) + " 0 0")
with open("tests/epd/arasan21.epd", "r", encoding="utf-8") as wacfile:
    for line in wacfile:
        epd = line.split()
        fens.append(" ".join(epd[:4]) + " 0 0")


@pytest.mark.parametrize("depth", range(1, 20))
def test_quiescence_mo(depth):
    for fen in fens:
        q1_result = quiescence(
            Config(
                {
                    "qs_move_ordering_fn": move_ordering.no_ordering,
                    "eval_fn": evaluation.eval_simple,
                    "use_qs_transposition_table": False,
                    "quiescence_depth": depth,
                }
            ),
            board.from_fen(fen),
            depth,
            deque(),
            -VALUE_MAX,
            VALUE_MAX,
        )
        q2_result = quiescence(
            Config(
                {
                    "qs_move_ordering_fn": move_ordering.qs_ordering,
                    "eval_fn": evaluation.eval_simple,
                    "use_qs_transposition_table": False,
                    "quiescence_depth": depth,
                }
            ),
            board.from_fen(fen),
            depth,
            deque(),
            -VALUE_MAX,
            VALUE_MAX,
        )
        assert q1_result.value == q2_result.value


@pytest.mark.parametrize("depth", range(9, 13))
def test_quiescence_depth(depth):
    for fen in fens:
        q1_result = quiescence(
            Config(
                {
                    "qs_move_ordering_fn": move_ordering.qs_ordering,
                    "eval_fn": evaluation.eval_simple,
                    "use_qs_transposition_table": False,
                    "quiescence_depth": depth,
                }
            ),
            board.from_fen(fen),
            depth,
            deque(),
            -VALUE_MAX,
            VALUE_MAX,
        )
        q2_result = quiescence(
            Config(
                {
                    "qs_move_ordering_fn": move_ordering.qs_ordering,
                    "eval_fn": evaluation.eval_simple,
                    "use_qs_transposition_table": False,
                    "quiescence_depth": 50,
                }
            ),
            board.from_fen(fen),
            50,
            deque(),
            -VALUE_MAX,
            VALUE_MAX,
        )
        assert q1_result.value == q2_result.value
