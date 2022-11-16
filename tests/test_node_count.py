"""
TestNodeCount
"""

from collections import deque
import unittest
from .win_at_chess import win_at_chess
import src.engine.board as board
from src.engine.algorithms import minimax, alphabeta, negac
from src.engine.constants import VALUE_MAX
from src.engine.transposition_table import TranspositionTable
from src.engine import move_ordering
from src.engine import evaluation


class TestNodeCount(unittest.TestCase):
    fens = win_at_chess[:50]

    def test_negac(self):
        depth = 3
        for fen in self.fens:
            negac_result = negac(
                board.from_fen(fen),
                depth,
                deque(),
                evaluation.eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                None,
                None,
            )
            mvv_lva_result = alphabeta(
                board.from_fen(fen),
                depth,
                deque(),
                evaluation.eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                None,
                move_ordering.mvv_lva,
            )
            print(f"{fen}: {negac_result.children} | {mvv_lva_result.children}")
            self.assertTrue(
                negac_result.children <= mvv_lva_result.children
            )

    def test_tt(self):
        depth = 6
        for fen in [
            "4r3/k3P3/p6p/1pn4P/2p1R3/P2n2P1/1P3P2/3R2K1 w - - 1 44",
            "4r3/3kP3/p4P1P/1p4p1/8/P1pnR3/7K/8 b - - 1 52",
            "6k1/3n2p1/r3p2p/6N1/2n5/2N3P1/P3PK1P/1R6 w - - 0 35",
            "8/5kp1/2r1p2p/8/P7/1RN1n1P1/4P1KP/8 w - - 5 43",
        ]:
            tt_result = alphabeta(
                board.from_fen(fen),
                depth,
                deque(),
                evaluation.eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                None,
                move_ordering.mvv_lva,
            )
            mvv_lva_result = alphabeta(
                board.from_fen(fen),
                depth,
                deque(),
                evaluation.eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                None,
                move_ordering.mvv_lva,
            )
            print(f"{fen}: {tt_result.children} | {mvv_lva_result.children}")
            self.assertTrue(
                tt_result.children <= mvv_lva_result.children
            )

    def test_mvv_lva(self):
        depth = 3
        for fen in self.fens:
            alphabeta_result = alphabeta(
                board.from_fen(fen),
                depth,
                deque(),
                evaluation.eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                None,
                None,
            )
            mvv_lva_result = alphabeta(
                board.from_fen(fen),
                depth,
                deque(),
                evaluation.eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                None,
                move_ordering.mvv_lva,
            )
            print(f"{fen}: {mvv_lva_result.children} | {alphabeta_result.children}")
            self.assertTrue(
                mvv_lva_result.children <= alphabeta_result.children
            )

    def test_minimax(self):
        depth = 3
        for fen in self.fens:
            alphabeta_result = alphabeta(
                board.from_fen(fen),
                depth,
                deque(),
                evaluation.eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                None,
                None,
            )
            minimax_result = minimax(
                board.from_fen(fen),
                depth,
                deque(),
                evaluation.eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                None,
                None,
            )
            print(f"{fen}: {alphabeta_result.children} | {minimax_result.children}")
            self.assertTrue(
                alphabeta_result.children <= minimax_result.children
            )


if __name__ == "__main__":
    unittest.main()
