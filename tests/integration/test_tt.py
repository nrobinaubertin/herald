"""Test transposition table.
"""

from collections import deque

import pytest

from herald import board, evaluation, move_ordering
from herald.transposition_table import TranspositionTable
from herald import algorithms
from herald.configuration import Config
from herald.constants import VALUE_MAX
from herald.data_structures import MoveType, to_uci

tt_fens = []
with open("tests/epd/transposition_table.epd", "r") as tt_file:
    for line in tt_file:
        epd = line.split()
        tt_fens.append(" ".join(epd[:4]) + " 0 0")

depths = [1, 2, 3, 4, 5, 6, 7]

# This test equivalence between w/ and w/o tt
@pytest.mark.parametrize("fen,depth", tuple([l1, l2] for l2 in depths for l1 in tt_fens))
def test_tt_equivalence(fen, depth):
    alphabeta_result = algorithms.alphabeta(
        Config(
            {
                "alg_fn": algorithms.alphabeta,
                "eval_fn": evaluation.eval_new,
                "move_ordering_fn": move_ordering.fast_mvv_lva,
                "qs_move_ordering_fn": move_ordering.qs_ordering,
                "quiescence_depth": 19,
                "quiescence_search": False,
                "use_qs_transposition_table": False,
                "use_transposition_table": False,
            }
        ),
        board.from_fen(fen),
        depth,
        deque(),
        MoveType.LEGAL,
        -VALUE_MAX,
        VALUE_MAX,
    )
    alphabeta_tt_result = algorithms.alphabeta(
        Config(
            {
                "alg_fn": algorithms.alphabeta,
                "eval_fn": evaluation.eval_new,
                "move_ordering_fn": move_ordering.fast_mvv_lva,
                "qs_move_ordering_fn": move_ordering.qs_ordering,
                "quiescence_depth": 19,
                "quiescence_search": False,
                "use_qs_transposition_table": False,
                "use_transposition_table": True,
            }
        ),
        board.from_fen(fen),
        depth,
        deque(),
        MoveType.LEGAL,
        -VALUE_MAX,
        VALUE_MAX,
    )
    assert alphabeta_tt_result.value == alphabeta_result.value
    assert (
        f"{fen}: {','.join([to_uci(x) for x in alphabeta_tt_result.pv])}"
        == f"{fen}: {','.join([to_uci(x) for x in alphabeta_result.pv])}"
    )
