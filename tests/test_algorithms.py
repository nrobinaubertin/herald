"""
TestAlgorithms
We test algorithms by comparing results to the minimax algorithm who's well known.
"""

from collections import deque
import unittest
from itertools import product
from .win_at_chess import win_at_chess
import src.engine.board as board
from src.engine.algorithms import minimax, alphabeta
from src.engine.constants import VALUE_MAX
from src.engine.transposition_table import TranspositionTable
from src.engine import move_ordering


class TestAlgorithms(unittest.TestCase):
    depth: int = 2
    fens = win_at_chess[:50]

    def test_alphabeta_mvv_lva_mo_tt(self):
        for fen in self.fens:
            minimax_result = minimax(board.from_fen(fen), self.depth, deque())
            alphabeta_result = alphabeta(
                board.from_fen(fen),
                -VALUE_MAX,
                VALUE_MAX,
                self.depth,
                deque(),
                TranspositionTable({}),
                move_ordering.mvv_lva,
            )
            self.assertEqual(minimax_result.value, alphabeta_result.value)
            self.assertEqual(minimax_result.pv, alphabeta_result.pv)

    def test_alphabeta_simple_mo_tt(self):
        for fen in self.fens:
            minimax_result = minimax(board.from_fen(fen), self.depth, deque())
            alphabeta_result = alphabeta(
                board.from_fen(fen),
                -VALUE_MAX,
                VALUE_MAX,
                self.depth,
                deque(),
                TranspositionTable({}),
                move_ordering.simple,
            )
            self.assertEqual(minimax_result.value, alphabeta_result.value)
            self.assertEqual(minimax_result.pv, alphabeta_result.pv)

    def test_alphabeta_mvv_lva_mo(self):
        for fen in self.fens:
            minimax_result = minimax(board.from_fen(fen), self.depth, deque())
            alphabeta_result = alphabeta(
                board.from_fen(fen),
                -VALUE_MAX,
                VALUE_MAX,
                self.depth,
                deque(),
                None,
                move_ordering.mvv_lva,
            )
            self.assertEqual(minimax_result.value, alphabeta_result.value)
            self.assertEqual(minimax_result.pv, alphabeta_result.pv)

    def test_alphabeta_simple_mo(self):
        for fen in self.fens:
            minimax_result = minimax(board.from_fen(fen), self.depth, deque())
            alphabeta_result = alphabeta(
                board.from_fen(fen),
                -VALUE_MAX,
                VALUE_MAX,
                self.depth,
                deque(),
                None,
                move_ordering.simple,
            )
            self.assertEqual(minimax_result.value, alphabeta_result.value)
            self.assertEqual(minimax_result.pv, alphabeta_result.pv)


if __name__ == "__main__":
    unittest.main()
