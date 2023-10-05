"""Minimax algorithm.

This is used for testing purposes only.
It is way too slow but easy to understand. I'm using this to verify my alphabeta implementation.
"""

from typing import Iterable

from . import board, evaluation
from . import move_ordering
from .board import Board
from .configuration import Config
from .constants import COLOR, VALUE_MAX
from .data_structures import Move


# Simple minimax
def minimax(
    config: Config,
    b: Board,
    depth: int,
    pv: list[Move],
    gen_legal_moves: bool = False,
    alpha: int = 0,
    beta: int = 0,
) -> int:
    assert depth >= 0, depth

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return evaluation.evaluation(b.squares, b.remaining_material)

    best = None
    child_pv: list[Move] = []

    moves: Iterable[Move] = []
    if gen_legal_moves:
        moves = board.legal_moves(b)
    else:
        moves = board.pseudo_legal_moves(b)
    for move in move_ordering.fast_ordering(
        b,
        moves,
    ):
        curr_board = board.push(b, move)

        # return immediately if this is a king capture
        if move.is_king_capture:
            return VALUE_MAX * b.turn

        # if the king is in check after we move
        # then it's a bad move (we will lose the game)
        if board.king_is_in_check(
            curr_board,
            curr_board.invturn,
        ):
            continue

        value = minimax(
            config,
            curr_board,
            depth - 1,
            child_pv,
            False,
        )

        if b.turn == COLOR.WHITE:
            if best is None or value > best:
                best = value
                pv.clear()
                pv.append(move)
                pv += child_pv
        else:
            if best is None or value < best:
                best = value
                pv.clear()
                pv.append(move)
                pv += child_pv

    if best is not None:
        return best

    # no "best" found
    # should happen only in case of stalemate/checkmate
    if board.is_square_attacked(
        b.squares,
        b.king_squares[b.turn],
        b.invturn,
    ):
        return VALUE_MAX * b.turn * -1
    return 0
