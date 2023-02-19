"""Test algorithms equivalence.

We test algorithms by comparing results to the minimax algorithm who's well known.
When comparing move ordering functions, we cannot compare pvs
"""

from collections import deque

import pytest

from herald import algorithms, board, evaluation, move_ordering, quiescence
from herald.algorithms import alphabeta, minimax
from herald.configuration import Config
from herald.constants import VALUE_MAX
from herald.data_structures import to_uci

win_at_chess = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"]
with open("tests/epd/wac.epd", "r") as wacfile:
    for line in wacfile:
        epd = line.split()
        win_at_chess.append(" ".join(epd[:4]) + " 0 0")

fens = win_at_chess
depths = [1, 2, 3, 4]


# This test equivalence between raw alphabeta
# and alphabeta with fast_mvv_lva move ordering
# This test can sometime fail. Why ? Question for later !
@pytest.mark.parametrize("fen", fens)
@pytest.mark.parametrize("depth", (1, 2, 3))
def test_fast_mvv_lva(fen, depth):
    alphabeta_result = alphabeta(
        Config(
            {
                "move_ordering_fn": move_ordering.no_ordering,
                "eval_fn": evaluation.eval_simple,
                "use_transposition_table": False,
                "use_qs_transposition_table": False,
                "use_move_tt": False,
            }
        ),
        board.from_fen(fen),
        depth,
        deque(),
        False,
        -VALUE_MAX,
        VALUE_MAX,
    )
    alphabeta_fast_mvv_lva_result = alphabeta(
        Config(
            {
                "move_ordering_fn": move_ordering.fast_mvv_lva,
                "eval_fn": evaluation.eval_simple,
                "use_transposition_table": False,
                "use_qs_transposition_table": False,
                "use_move_tt": False,
            }
        ),
        board.from_fen(fen),
        depth,
        deque(),
        False,
        -VALUE_MAX,
        VALUE_MAX,
    )
    assert alphabeta_fast_mvv_lva_result.value == alphabeta_result.value


# This test equivalence between raw alphabeta and minimax
@pytest.mark.parametrize("fen", fens)
@pytest.mark.parametrize("depth", (1, 2, 3))
def test_alphabeta(fen, depth):
    minimax_result = minimax(
        Config(
            {
                "move_ordering_fn": move_ordering.no_ordering,
                "eval_fn": evaluation.eval_simple,
                "use_transposition_table": False,
                "use_qs_transposition_table": False,
                "use_move_tt": False,
            }
        ),
        board.from_fen(fen),
        depth,
        deque(),
        False,
    )
    alphabeta_result = alphabeta(
        Config(
            {
                "move_ordering_fn": move_ordering.no_ordering,
                "eval_fn": evaluation.eval_simple,
                "use_transposition_table": False,
                "use_qs_transposition_table": False,
                "use_move_tt": False,
            }
        ),
        board.from_fen(fen),
        depth,
        deque(),
        False,
        -VALUE_MAX,
        VALUE_MAX,
    )
    assert minimax_result.value == alphabeta_result.value
    assert (
        f"{fen}: {','.join([to_uci(x) for x in minimax_result.pv])}"
        == f"{fen}: {','.join([to_uci(x) for x in alphabeta_result.pv])}"
    )


@pytest.mark.parametrize("fen", fens)
@pytest.mark.parametrize("depth", (1, 2, 3, 4))
def test_killer_move(fen, depth):
    r1 = alphabeta(
        Config(
            {
                "alg_fn": algorithms.alphabeta,
                "move_ordering_fn": move_ordering.fast_mvv_lva,
                "qs_move_ordering_fn": move_ordering.qs_ordering,
                "eval_fn": evaluation.eval_new,
                "quiescence_search": True,
                "quiescence_depth": 50,
                "use_transposition_table": True,
                "use_move_tt": True,
                "quiescence_fn": quiescence.quiescence,
            }
        ),
        board.from_fen(fen),
        depth,
        deque(),
        False,
        -VALUE_MAX,
        VALUE_MAX,
    )
    r2 = alphabeta(
        Config(
            {
                "alg_fn": algorithms.alphabeta,
                "move_ordering_fn": move_ordering.fast_mvv_lva,
                "qs_move_ordering_fn": move_ordering.qs_ordering,
                "eval_fn": evaluation.eval_new,
                "quiescence_search": True,
                "quiescence_depth": 50,
                "use_transposition_table": True,
                "use_move_tt": False,
                "quiescence_fn": quiescence.quiescence,
            }
        ),
        board.from_fen(fen),
        depth,
        deque(),
        False,
        -VALUE_MAX,
        VALUE_MAX,
    )
    assert r1.value == r2.value
    assert (
        f"{fen}: {','.join([to_uci(x) for x in r1.pv])}"
        == f"{fen}: {','.join([to_uci(x) for x in r2.pv])}"
    )
