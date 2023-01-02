"""
TestBoard
We test our move generation using the perft algorithm
"""

import unittest

import src.engine.board as board
from src.engine.data_structures import Board, to_uci

from .win_at_chess import wac_moves, win_at_chess


class TestAlgorithms(unittest.TestCase):
    def execute(self, b: Board, depth: int):
        if depth == 1:
            return len(list(board.legal_moves(b)))

        nodes = 0
        for move in board.legal_moves(b):
            curr_board = board.push(b, move)
            nodes += self.execute(curr_board, depth - 1)

        return nodes

    # https://www.chessprogramming.org/Perft_Results#Initial_Position
    def test_perft_startpos(self):
        # too long for depth = 5
        nodes = self.execute(board.from_fen("startpos"), 4)
        self.assertEqual(nodes, 197281)

    # https://www.chessprogramming.org/Perft_Results#Position_2
    def test_perft_pos2(self):
        # depth = 4 doesn't work because we don't have underpromotions
        nodes = self.execute(
            board.from_fen("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 0"),
            3,
        )
        self.assertEqual(nodes, 97862)

    # https://www.chessprogramming.org/Perft_Results#Position_3
    def test_perft_pos3(self):
        # depth = 6 doesn't work because we don't have underpromotions
        nodes = self.execute(board.from_fen("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 0"), 5)
        self.assertEqual(nodes, 674624)

    # Doesn't work because we don't have underpromotions
    # https://www.chessprogramming.org/Perft_Results#Position_4
    # def test_perft_pos4(self):
    #     nodes = self.execute(board.from_fen("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1"), 4)
    #     self.assertEqual(nodes, 422333)

    # Doesn't work because we don't have underpromotions
    # https://www.chessprogramming.org/Perft_Results#Position_5
    # def test_perft_pos5(self):
    #     nodes = self.execute(board.from_fen("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"), 3)
    #     self.assertEqual(nodes, 62379)

    # https://www.chessprogramming.org/Perft_Results#Position_6
    def test_perft_pos6(self):
        # too long for depth = 4
        nodes = self.execute(
            board.from_fen(
                "r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10"
            ),
            3,
        )
        self.assertEqual(nodes, 89890)

    # testing the number of moves available
    # for each position in win_at_chess
    # (based on herald without underpromotion)
    # The goal is to know what is going wrong fast
    def test_moves(self):
        self.maxDiff = None
        for i, fen in enumerate(win_at_chess):
            b = board.from_fen(fen)
            self.assertEqual(",".join([to_uci(m) for m in board.legal_moves(b)]), wac_moves[i])


if __name__ == "__main__":
    unittest.main()
