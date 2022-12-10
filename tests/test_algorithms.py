"""
TestAlgorithms
We test algorithms by comparing results to the minimax algorithm who's well known.
"""

from collections import deque
import unittest
from .win_at_chess import win_at_chess
import src.engine.board as board
from src.engine.algorithms import minimax, alphabeta, negac
from src.engine.constants import VALUE_MAX
from src.engine.evaluation import eval_simple
from src.engine import move_ordering
from src.engine.data_structures import to_uci


class TestAlgorithms(unittest.TestCase):
    fens = win_at_chess[:50]

    # This test equivalence between negac and alphabeta w/ mvv-lva
    def test_negac(self):
        depth = 4
        for fen in self.fens:
            negac_result = negac(
                board.from_fen(fen),
                depth,
                deque(),
                eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                None,
                move_ordering.mvv_lva,
            )
            alphabeta_mvv_lva_result = alphabeta(
                board.from_fen(fen),
                depth,
                deque(),
                eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                None,
                move_ordering.mvv_lva,
            )
            self.assertEqual(
                negac_result.value,
                alphabeta_mvv_lva_result.value
            )
            self.assertEqual(
                f"{fen}: {','.join([to_uci(x) for x in negac_result.pv])}",
                f"{fen}: {','.join([to_uci(x) for x in alphabeta_mvv_lva_result.pv])}",
            )

    # This test equivalence between raw alphabeta
    # and alphabeta with mvv_lva move ordering
    def test_mvv_lva(self):
        depth = 4
        for fen in self.fens:
            alphabeta_result = alphabeta(
                board.from_fen(fen),
                depth,
                deque(),
                eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                None,
                None,
            )
            alphabeta_mvv_lva_result = alphabeta(
                board.from_fen(fen),
                depth,
                deque(),
                eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                None,
                move_ordering.mvv_lva,
            )
            self.assertEqual(
                alphabeta_mvv_lva_result.value,
                alphabeta_result.value
            )
            self.assertEqual(
                f"{fen}: {','.join([to_uci(x) for x in alphabeta_mvv_lva_result.pv])}",
                f"{fen}: {','.join([to_uci(x) for x in alphabeta_result.pv])}",
            )

    # This test equivalence between raw alphabeta and minimax
    def test_alphabeta(self):
        depth = 3
        for fen in self.fens:
            minimax_result = minimax(
                board.from_fen(fen),
                depth,
                deque(),
                eval_simple
            )
            alphabeta_result = alphabeta(
                board.from_fen(fen),
                depth,
                deque(),
                eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                None,
                None,
            )
            self.assertEqual(minimax_result.value, alphabeta_result.value)
            self.assertEqual(
                f"{fen}: {','.join([to_uci(x) for x in minimax_result.pv])}",
                f"{fen}: {','.join([to_uci(x) for x in alphabeta_result.pv])}",
            )


if __name__ == "__main__":
    unittest.main()
