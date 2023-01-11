"""Test algorithms equivalence.

We test algorithms by comparing results to the minimax algorithm who's well known.
When comparing move ordering functions, we cannot compare pvs
"""

from collections import deque

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


def test_fast_mvv_lva():
    depth = 3
    for fen in win_at_chess:
        futility_result = alphabeta(
            Config(
                {
                    "move_ordering_fn": move_ordering.fast_mvv_lva,
                    "eval_fn": evaluation.eval_simple,
                }
            ),
            board.from_fen(fen),
            depth,
            deque(),
            MoveType.LEGAL,
            -VALUE_MAX,
            VALUE_MAX,
        )
        base_result = alphabeta(
            Config(
                {
                    "move_ordering_fn": move_ordering.mvv_lva,
                    "eval_fn": evaluation.eval_simple,
                }
            ),
            board.from_fen(fen),
            depth,
            deque(),
            MoveType.LEGAL,
            -VALUE_MAX,
            VALUE_MAX,
        )
        assert futility_result.value == base_result.value


def test_futility():
    depth = 5
    for fen in win_at_chess:
        futility_result = alphabeta(
            Config(
                {
                    "alg_fn": alphabeta,
                    "eval_fn": evaluation.eval_new,
                    "futility_depth": 3,
                    "futility_pruning": True,
                    "move_ordering_fn": move_ordering.fast_mvv_lva,
                    "qs_move_ordering_fn": move_ordering.qs_ordering,
                    "quiescence_depth": 5,
                    "quiescence_search": True,
                    "use_qs_transposition_table": True,
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
        base_result = alphabeta(
            Config(
                {
                    "alg_fn": alphabeta,
                    "eval_fn": evaluation.eval_new,
                    "futility_depth": 0,
                    "futility_pruning": False,
                    "move_ordering_fn": move_ordering.fast_mvv_lva,
                    "qs_move_ordering_fn": move_ordering.qs_ordering,
                    "quiescence_depth": 5,
                    "quiescence_search": True,
                    "use_qs_transposition_table": True,
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
        assert futility_result.value == base_result.value
        assert (
            f"{fen}: {','.join([to_uci(x) for x in futility_result.pv])}"
            == f"{fen}: {','.join([to_uci(x) for x in base_result.pv])}"
        )


# This test equivalence between raw alphabeta
# and alphabeta with mvv_lva move ordering
def test_mvv_lva():
    depth = 3
    for fen in win_at_chess:
        alphabeta_result = alphabeta(
            Config(
                {
                    "move_ordering_fn": move_ordering.no_ordering,
                    "eval_fn": evaluation.eval_simple,
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
def test_alphabeta():
    depth = 3
    for fen in win_at_chess:
        minimax_result = minimax(
            Config(
                {
                    "move_ordering_fn": move_ordering.no_ordering,
                    "eval_fn": evaluation.eval_simple,
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
