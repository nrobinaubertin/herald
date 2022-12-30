"""
TestSelfPlay
"""

from collections import deque
import unittest
from .win_at_chess import win_at_chess
import src.engine.board as board
from src.engine.constants import COLOR
from src.engine.algorithms import minimax, alphabeta
from src.engine.evaluation import eval_simple, eval_new, eval_pst
from src.engine import move_ordering
from src.engine.data_structures import to_uci, MoveType
from src.engine.configuration import Config
from src.engine.iterative_deepening import itdep


class TestSelfPlay(unittest.TestCase):

    def _play(self, config: Config, b: board.Board):
        res = itdep(
            b,
            config,
            max_depth=config._config["depth"],
            print_uci=True,
        )
        if res is None or res.move is None:
            nb = b
            move = None
        else:
            nb = board.push(b, res.move)
            move = res.move
        return move, nb

    def _match(self, config_w: Config, config_b: Config):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        current_board = board.from_fen(fen)

        while True:
            if current_board.half_move > 10:
                if abs(eval_simple(current_board)) > 200:
                    return COLOR.WHITE if eval_simple(current_board) > 0 else COLOR.BLACK
                return 0
            move, current_board = self._play(
                config_w if current_board.turn == COLOR.WHITE else config_b,
                current_board,
            )
            if move is None:
                return current_board.turn * -1
            else:
                print(board.to_string(current_board))
                print(board.to_fen(current_board))

    def test_plop(self):
        score = {0: 0, COLOR.WHITE: 0, COLOR.BLACK: 0}
        for _ in range(100):
            res = self._match(
                Config({
                    "alg_fn": alphabeta,
                    "move_ordering_fn": move_ordering.random,
                    "qs_move_ordering_fn": move_ordering.fast_mvv_lva,
                    "eval_fn": eval_new,
                    "use_transposition_table": True,
                    "use_qs_transposition_table": True,
                    "quiescence_search": True,
                    "quiescence_depth": 5,
                    "depth": 4,
                }),
                Config({
                    "alg_fn": alphabeta,
                    "move_ordering_fn": move_ordering.random,
                    "qs_move_ordering_fn": move_ordering.qs_ordering,
                    "eval_fn": eval_new,
                    "use_transposition_table": True,
                    "use_qs_transposition_table": True,
                    "quiescence_search": True,
                    "quiescence_depth": 5,
                    "depth": 4,
                }),
            )
            score[res] += 1
        print(score)
        self.assertTrue(score[COLOR.BLACK] + score[0]/2 > 60)

    def test_eval_new(self):
        score = {0: 0, COLOR.WHITE: 0, COLOR.BLACK: 0}
        for _ in range(10):
            res = self._match(
                Config({
                    "alg_fn": alphabeta,
                    "move_ordering_fn": move_ordering.random,
                    "eval_fn": eval_pst,
                    "use_transposition_table": False,
                    "quiescence_search": False,
                    "quiescence_depth": 0,
                    "depth": 5,
                }),
                Config({
                    "alg_fn": alphabeta,
                    "move_ordering_fn": move_ordering.random,
                    "eval_fn": eval_new,
                    "use_transposition_table": True,
                    "quiescence_search": True,
                    "quiescence_depth": 5,
                    "depth": 4,
                }),
            )
            score[res] += 1
        print(score)
        self.assertTrue(score[COLOR.BLACK] + score[0]/2 > 60)

    def test_quiescence(self):
        score = {0: 0, COLOR.WHITE: 0, COLOR.BLACK: 0}
        for _ in range(50):
            res = self._match(
                Config({
                    "alg_fn": alphabeta,
                    "move_ordering_fn": move_ordering.random,
                    "eval_fn": eval_simple,
                    "use_transposition_table": False,
                    "depth": 3,
                }),
                Config({
                    "alg_fn": alphabeta,
                    "move_ordering_fn": move_ordering.mvv_lva,
                    "eval_fn": eval_simple,
                    "use_transposition_table": True,
                    "quiescence_search": True,
                    "quiescence_depth": 5,
                    "depth": 3,
                }),
            )
            score[res] += 1
        print(score)
        self.assertTrue(score[COLOR.BLACK] + score[0]/2 > 30)
