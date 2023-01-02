"""
TestNodeCount
:warning: This test should not be used for the time being
"""

import unittest
from collections import deque

import src.engine.board as board
from src.engine import evaluation, move_ordering
from src.engine.algorithms import alphabeta, minimax, negac
from src.engine.constants import VALUE_MAX
from src.engine.iterative_deepening import itdep
from src.engine.transposition_table import TranspositionTable

from .win_at_chess import win_at_chess


class TestNodeCount(unittest.TestCase):
    fens = win_at_chess[:50]

    def test_iterative_deepening(self):
        depth = 5
        tot_best_move = 0
        tot_itdep = 0
        for fen in self.fens:
            itdep_result = itdep(
                board.from_fen(fen),
                alphabeta,
                movetime=0,
                max_depth=depth,
                print_uci=False,
            )
            tot_itdep += itdep_result.nodes
            print(f"{fen}: {itdep_result.nodes}")
        print(f"TOTAL: {tot_best_move} | {tot_itdep}")

    def test_negac(self):
        depth = 4
        tot_negac = 0
        for fen in win_at_chess[:100]:
            negac_result = negac(
                board.from_fen(fen),
                depth,
                deque(),
                evaluation.eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                TranspositionTable({}),
                move_ordering.mvv_lva,
            )
            tot_negac += negac_result.children
            # print(f"{fen}: {negac_result.children}")
        print(f"TOTAL: {tot_negac}")

    def test_tt(self):
        depth = 4
        tot_tt = 0
        for fen in self.fens:
            tt_result = alphabeta(
                board.from_fen(fen),
                depth,
                deque(),
                evaluation.eval_simple,
                -VALUE_MAX,
                VALUE_MAX,
                TranspositionTable({}),
                move_ordering.mvv_lva,
            )
            tot_tt += tt_result.children
        print(f"TOTAL: {tot_tt}")

    def test_move_ordering(self):
        depth = 3
        for fen in self.fens:
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
            print(f"{fen}: {mvv_lva_result.children}")

    def test_minimax(self):
        depth = 3
        for fen in self.fens:
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
            print(f"{fen}: {minimax_result.children}")


if __name__ == "__main__":
    unittest.main()
