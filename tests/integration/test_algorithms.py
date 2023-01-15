"""Test algorithms equivalence.

We test algorithms by comparing results to the minimax algorithm who's well known.
When comparing move ordering functions, we cannot compare pvs
"""

from collections import deque

import pytest

from herald import board, evaluation, move_ordering
from herald.algorithms import alphabeta, minimax
from herald.configuration import Config
from herald.constants import VALUE_MAX
from herald.data_structures import MoveType, to_uci

win_at_chess = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"]
with open("tests/epd/wac.epd", "r") as wacfile:
    for line in wacfile:
        epd = line.split()
        win_at_chess.append(" ".join(epd[:4]) + " 0 0")


# This test equivalence between raw alphabeta
# and alphabeta with fast_mvv_lva move ordering
@pytest.mark.parametrize("depth", range(1, 4))
def test_fast_mvv_lva(depth):
    for fen in win_at_chess:
        alphabeta_result = alphabeta(
            Config(
                {
                    "move_ordering_fn": move_ordering.no_ordering,
                    "eval_fn": evaluation.eval_simple,
                    "use_transposition_table": False,
                    "use_qs_transposition_table": False,
                }
            ),
            board.from_fen(fen),
            depth,
            deque(),
            MoveType.LEGAL,
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
                }
            ),
            board.from_fen(fen),
            depth,
            deque(),
            MoveType.LEGAL,
            -VALUE_MAX,
            VALUE_MAX,
        )
        assert alphabeta_fast_mvv_lva_result.value == alphabeta_result.value


# This test equivalence between raw alphabeta
# and alphabeta with mvv_lva move ordering
@pytest.mark.parametrize("depth", range(1, 4))
def test_mvv_lva(depth):
    for fen in win_at_chess:
        alphabeta_result = alphabeta(
            Config(
                {
                    "move_ordering_fn": move_ordering.no_ordering,
                    "eval_fn": evaluation.eval_simple,
                    "use_transposition_table": False,
                    "use_qs_transposition_table": False,
                }
            ),
            board.from_fen(fen),
            depth,
            deque(),
            MoveType.LEGAL,
            -VALUE_MAX,
            VALUE_MAX,
        )
        alphabeta_mvv_lva_result = alphabeta(
            Config(
                {
                    "move_ordering_fn": move_ordering.mvv_lva,
                    "eval_fn": evaluation.eval_simple,
                    "use_transposition_table": False,
                    "use_qs_transposition_table": False,
                }
            ),
            board.from_fen(fen),
            depth,
            deque(),
            MoveType.LEGAL,
            -VALUE_MAX,
            VALUE_MAX,
        )
        assert alphabeta_mvv_lva_result.value == alphabeta_result.value


# This test equivalence between raw alphabeta and minimax
@pytest.mark.parametrize("depth", range(1, 4))
def test_alphabeta(depth):
    for fen in win_at_chess:
        minimax_result = minimax(
            Config(
                {
                    "move_ordering_fn": move_ordering.no_ordering,
                    "eval_fn": evaluation.eval_simple,
                    "use_transposition_table": False,
                    "use_qs_transposition_table": False,
                }
            ),
            board.from_fen(fen),
            depth,
            deque(),
            MoveType.LEGAL,
        )
        alphabeta_result = alphabeta(
            Config(
                {
                    "move_ordering_fn": move_ordering.no_ordering,
                    "eval_fn": evaluation.eval_simple,
                    "use_transposition_table": False,
                    "use_qs_transposition_table": False,
                }
            ),
            board.from_fen(fen),
            depth,
            deque(),
            MoveType.LEGAL,
            -VALUE_MAX,
            VALUE_MAX,
        )
        assert minimax_result.value == alphabeta_result.value
        assert (
            f"{fen}: {','.join([to_uci(x) for x in minimax_result.pv])}"
            == f"{fen}: {','.join([to_uci(x) for x in alphabeta_result.pv])}"
        )
