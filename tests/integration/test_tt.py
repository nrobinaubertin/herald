"""Test transposition table."""

from collections import deque

import pytest

from herald import algorithms, board, evaluation, move_ordering, quiescence
from herald.configuration import Config
from herald.constants import VALUE_MAX
from herald.data_structures import MoveType, to_uci

tt_fens = []
with open("tests/epd/transposition_table.epd", "r") as tt_file:
    for line in tt_file:
        epd = line.split()
        tt_fens.append(" ".join(epd[:4]) + " 0 0")

depths = [1, 2, 3, 4, 5, 6, 7]
use_qs = [True, False]
eval_fn = [evaluation.eval_simple, evaluation.eval_new]


# This test equivalence between w/ and w/o tt
@pytest.mark.parametrize("fen,depth,use_qs,eval_fn", tuple([l1, l2, l3, l4] for l2 in depths for l1 in tt_fens for l3 in use_qs for l4 in eval_fn))
def test_tt_equivalence(fen, depth, use_qs, eval_fn):
    alphabeta_result = algorithms.alphabeta(
        Config(
            {
                "alg_fn": algorithms.alphabeta,
                "eval_fn": eval_fn,
                "move_ordering_fn": move_ordering.fast_mvv_lva,
                "qs_move_ordering_fn": move_ordering.qs_ordering,
                "quiescence_depth": 25,
                "quiescence_search": use_qs,
                "quiescence_fn": quiescence.quiescence,
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
                "eval_fn": eval_fn,
                "move_ordering_fn": move_ordering.fast_mvv_lva,
                "qs_move_ordering_fn": move_ordering.qs_ordering,
                "quiescence_depth": 25,
                "quiescence_search": use_qs,
                "quiescence_fn": quiescence.quiescence,
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
    # assert (
    #     f"{fen}: {','.join([to_uci(x) for x in alphabeta_tt_result.pv])}"
    #     == f"{fen}: {','.join([to_uci(x) for x in alphabeta_result.pv])}"
    # )
