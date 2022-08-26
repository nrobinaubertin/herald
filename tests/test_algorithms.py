"""
TestAlgorithms
We test algorithms by comparing results to the minimax algorithm who's well known.
"""

from collections import deque
import unittest
from .win_at_chess import win_at_chess
import src.engine.board as board
from src.engine.algorithms import minimax, alphabeta, alphabeta_mo, alphabeta_mo_tt
from src.engine.constants import VALUE_MAX
from src.engine.transposition_table import TranspositionTable


class TestAlgorithms(unittest.TestCase):
    def test_alphabeta(self):
        depth = 2
        for fen in win_at_chess[:10]:
            minimax_result = minimax(board.from_fen(fen), depth, deque())
            alphabeta_result = alphabeta(
                board.from_fen(fen), -VALUE_MAX, VALUE_MAX, depth, deque()
            )
            self.assertEqual(minimax_result.value, alphabeta_result.value)
            self.assertEqual(minimax_result.pv, alphabeta_result.pv)

    def test_alphabeta_mo(self):
        depth = 2
        for fen in win_at_chess[:10]:
            minimax_result = minimax(board.from_fen(fen), depth, deque())
            alphabeta_mo_result = alphabeta_mo(
                board.from_fen(fen), -VALUE_MAX, VALUE_MAX, depth, deque()
            )
            self.assertEqual(minimax_result.value, alphabeta_mo_result.value)
            self.assertEqual(minimax_result.pv, alphabeta_mo_result.pv)

    def test_alphabeta_mo_tt(self):
        depth = 2
        for fen in win_at_chess[:10]:
            minimax_result = minimax(board.from_fen(fen), depth, deque())
            alphabeta_mo_tt_result = alphabeta_mo_tt(
                board.from_fen(fen), -VALUE_MAX, VALUE_MAX, depth, deque(), TranspositionTable({})
            )
            self.assertEqual(minimax_result.value, alphabeta_mo_tt_result.value)
            self.assertEqual(minimax_result.pv, alphabeta_mo_tt_result.pv)


if __name__ == "__main__":
    unittest.main()
