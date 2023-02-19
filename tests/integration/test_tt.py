"""Test transposition table."""

from collections import deque

import pytest

from herald import algorithms, board, evaluation, move_ordering, quiescence
from herald.configuration import Config
from herald.constants import VALUE_MAX

fens = []
with open("tests/epd/transposition_table.epd", "r") as tt_file:
    for line in tt_file:
        epd = line.split()
        fens.append(" ".join(epd[:4]) + " 0 0")


# This test equivalence between w/ and w/o tt
@pytest.mark.parametrize("fen", fens)
@pytest.mark.parametrize("depth", (1, 2, 3, 4, 5, 6, 7))
@pytest.mark.parametrize("use_qs", (True, False))
@pytest.mark.parametrize("eval_fn", (evaluation.eval_simple, evaluation.eval_new))
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
        False,
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
        False,
        -VALUE_MAX,
        VALUE_MAX,
    )
    assert alphabeta_tt_result.value == alphabeta_result.value
    # assert (
    #     f"{fen}: {','.join([to_uci(x) for x in alphabeta_tt_result.pv])}"
    #     == f"{fen}: {','.join([to_uci(x) for x in alphabeta_result.pv])}"
    # )
