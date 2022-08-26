"""
TestBoard
We test our move generation using the perft algorithm
"""

import unittest
import src.engine.board as board
from src.engine.data_structures import Board


class TestAlgorithms(unittest.TestCase):
    def execute(self, b: Board, depth: int):
        if depth == 1:
            return len(list(board.pseudo_legal_moves(b)))

        nodes = 0
        for move in board.moves(b):
            curr_board = board.push(b, move)
            nodes += self.execute(curr_board, depth - 1)

        return nodes

    def test_perft(self):
        nodes = self.execute(board.from_fen("startpos"), 4)
        # returns 197742
        # which is the correct number + 469 checks - 8 mats
        self.assertEqual(nodes, 197281)


if __name__ == "__main__":
    unittest.main()
