"""
TestTranspositionTable
We test the transposition table by comparing results with and without it
"""

from collections import deque
import unittest
from .win_at_chess import win_at_chess
import src.engine.board as board
from src.engine.algorithms import alphabeta, negac
from src.engine.constants import VALUE_MAX
from src.engine.transposition_table import TranspositionTable
from src.engine import move_ordering
from src.engine import evaluation
from src.engine.data_structures import to_uci


class TestTranspositionTable(unittest.TestCase):
    fens = win_at_chess[:50]

    def test_negac(self):
        depth = 4
        for fen in self.fens:
            negac_tt_result = negac(
                board.from_fen(fen),
                depth,
                deque(),
                evaluation.eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                TranspositionTable({}),
                None,
            )
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
            self.assertEqual(
                fen + ', ' + str(negac_tt_result.value),
                fen + ', ' + str(negac_result.value)
            )
            self.assertEqual(
                fen + ', ' + ' '.join([to_uci(x) for x in negac_tt_result.pv]),
                fen + ', ' + ' '.join([to_uci(x) for x in negac_result.pv]),
            )

    def test_alphabeta(self):
        depth = 4
        for fen in self.fens:
            alphabeta_tt_result = alphabeta(
                board.from_fen(fen),
                depth,
                deque(),
                evaluation.eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                TranspositionTable({}),
                None,
            )
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
            self.assertEqual(
                fen + ', ' + str(alphabeta_tt_result.value),
                fen + ', ' + str(alphabeta_result.value)
            )
            self.assertEqual(
                fen + ', ' + ' '.join([to_uci(x) for x in alphabeta_tt_result.pv]),
                fen + ', ' + ' '.join([to_uci(x) for x in alphabeta_result.pv]),
            )


if __name__ == "__main__":
    unittest.main()
