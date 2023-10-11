"""Minimax algorithm.

This is used for testing purposes only.
It is way too slow but easy to understand.
"""

from typing import Iterable

import board, evaluation
import move_ordering
from board import Board
from constants import COLOR, VALUE_MAX
from data_structures import Move


# Simple minimax
def minimax(
    *,
    b: Board,
    depth: int,
    pv: list[Move],
    gen_legal_moves: bool = False,
) -> int:
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
        if board.king_is_in_check(curr_board, curr_board.invturn):
            continue

        value = minimax(
            b=curr_board,
            depth=depth - 1,
            pv=child_pv,
            gen_legal_moves=False,
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
    # this means that we have no move available
    # should happen only in case of stalemate/checkmate

    # if the king square is attacked, it's a checkmate
    if board.king_is_in_check(b, b.turn):
        return VALUE_MAX * b.turn * -1

    # if the king square is not attacked, then it's a stalemate
    return 0
