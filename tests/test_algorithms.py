"""
TestAlgorithms
We test algorithms by comparing results to the minimax algorithm who's well known.
"""

from collections import deque
import unittest
from .win_at_chess import win_at_chess
import src.engine.board as board
from src.engine.algorithms import minimax, alphabeta, aspiration_window, negac
from src.engine.constants import VALUE_MAX
from src.engine.transposition_table import TranspositionTable
from src.engine import move_ordering


class TestAlgorithms(unittest.TestCase):
    fens = win_at_chess[:50]

    # This test equivalence between aspiration window and negac
    def test_negac(self):
        depth = 4
        for fen in self.fens:
            negac_result = negac(
                board.from_fen(fen),
                -VALUE_MAX,
                VALUE_MAX,
                depth,
                deque(),
                None,
                move_ordering.mvv_lva,
            )
            aspiration_window_result = aspiration_window(
                board.from_fen(fen),
                0,
                depth,
                deque(),
                None,
                move_ordering.mvv_lva,
            )
            self.assertEqual(negac_result.value, aspiration_window_result.value)
            self.assertEqual(negac_result.pv, aspiration_window_result.pv)

    # This test equivalence between aspiration window on alphabeta with mvv_lva move ordering and without the aspiration window
    def test_aspiration_window_mvv_lva_mo(self):
        depth = 4
        for fen in self.fens:
            alphabeta_mvv_lva_result = alphabeta(
                board.from_fen(fen),
                -VALUE_MAX,
                VALUE_MAX,
                depth,
                deque(),
                None,
                move_ordering.mvv_lva,
            )
            aspiration_window_result = aspiration_window(
                board.from_fen(fen),
                0,
                depth,
                deque(),
                None,
                move_ordering.mvv_lva,
            )
            self.assertEqual(alphabeta_mvv_lva_result.value, aspiration_window_result.value)
            self.assertEqual(alphabeta_mvv_lva_result.pv, aspiration_window_result.pv)

    # This test equivalence between raw alphabeta and alphabeta with mvv_lva move ordering
    def test_alphabeta_mvv_lva_mo(self):
        depth = 4
        for fen in self.fens:
            alphabeta_result = alphabeta(
                board.from_fen(fen),
                -VALUE_MAX,
                VALUE_MAX,
                depth,
                deque(),
                None,
                None,
            )
            alphabeta_mvv_lva_result = alphabeta(
                board.from_fen(fen),
                -VALUE_MAX,
                VALUE_MAX,
                depth,
                deque(),
                None,
                move_ordering.mvv_lva,
            )
            self.assertEqual(alphabeta_mvv_lva_result.value, alphabeta_result.value)
            self.assertEqual(alphabeta_mvv_lva_result.pv, alphabeta_result.pv)

    # This test equivalence between raw alphabeta and minimax
    def test_alphabeta(self):
        depth = 3
        for fen in self.fens:
            minimax_result = minimax(board.from_fen(fen), depth, deque())
            alphabeta_result = alphabeta(
                board.from_fen(fen),
                -VALUE_MAX,
                VALUE_MAX,
                depth,
                deque(),
                None,
                None,
            )
            self.assertEqual(minimax_result.value, alphabeta_result.value)
            self.assertEqual(minimax_result.pv, alphabeta_result.pv)


if __name__ == "__main__":
    unittest.main()
