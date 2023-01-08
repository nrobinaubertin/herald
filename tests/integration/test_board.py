"""
TestBoard
We test our move generation using the perft algorithm
"""

import pytest

from herald import board
from herald.data_structures import Board, to_uci

from ..win_at_chess import wac_moves, win_at_chess


def perft(b: Board, depth: int):
    if depth == 1:
        return len(list(board.legal_moves(b)))

    nodes = 0
    for move in board.legal_moves(b):
        curr_board = board.push(b, move)
        nodes += perft(curr_board, depth - 1)

    return nodes


@pytest.mark.parametrize("fen,depth,expected", [
    # https://www.chessprogramming.org/Perft_Results#Initial_Position
    ("startpos", 4, 197281),

    # https://www.chessprogramming.org/Perft_Results#Position_2
    # depth = 4 doesn't work because we don't have underpromotions
    ("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 0", 3, 97862),

    # https://www.chessprogramming.org/Perft_Results#Position_3
    ("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 0", 5, 674624),

    # https://www.chessprogramming.org/Perft_Results#Position_6
    ("r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10", 3, 89890),
])
def test_pos(fen, depth, expected):
    nodes = perft(board.from_fen(fen), depth)
    assert nodes == expected


# https://www.chessprogramming.org/Perft_Results#Position_4
@pytest.mark.skip(reason="Underpromotions not supported yet")
def test_perft_pos4():
    nodes = perft(board.from_fen("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1"), 4)
    assert nodes == 422333


# https://www.chessprogramming.org/Perft_Results#Position_5
@pytest.mark.skip(reason="Underpromotions not supported yet")
def test_perft_pos5():
    nodes = perft(board.from_fen("rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"), 3)
    assert nodes == 62379


# testing the number of moves available
# for each position in win_at_chess
# (based on herald without underpromotion)
# The goal is to know what is going wrong fast
def test_win_at_chess_positions():
    for i, fen in enumerate(win_at_chess):
        b = board.from_fen(fen)
        assert ",".join([to_uci(m) for m in board.legal_moves(b)]) == wac_moves[i]
