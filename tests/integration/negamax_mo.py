"""Negamax algorithm with move_ordering.

This is used for testing purposes only.
"""

from typing import Iterable

import board
import evaluation
import move_ordering
from board import Board
from constants import VALUE_MAX, COLOR_DIRECTION
from data_structures import Move


def negamax_mo(
    *,
    b: Board,
    depth: int,
    pv: list[Move],
    gen_legal_moves: bool = False,
    alpha: int = -VALUE_MAX,
    beta: int = VALUE_MAX,
) -> int:
    if depth == 0:
        return evaluation.evaluation(b.squares, b.remaining_material) * COLOR_DIRECTION[b.turn]

    best = None
    child_pv: list[Move] = []

    moves: Iterable[Move] = []
    if gen_legal_moves:
        moves = board.legal_moves(b)
    else:
        moves = board.pseudo_legal_moves(b)

    moves = move_ordering.fast_ordering(b, moves)

    for move in moves:
        # return immediately if this is a king capture
        if move.is_king_capture:
            pv.clear()
            pv.append(move)
            pv += child_pv
            return VALUE_MAX

        curr_board = board.push(b, move)

        # if the king is in check after we move
        # then it's a bad move (we will lose the game)
        if board.king_is_in_check(curr_board, b.turn):
            continue

        value = -negamax_mo(
            b=curr_board,
            depth=depth - 1,
            pv=child_pv,
            gen_legal_moves=False,
            alpha=-beta,
            beta=-alpha,
        )

        if best is None or value > best:
            best = value
            pv.clear()
            pv.append(move)
            pv += child_pv
        alpha = max(alpha, value)
        if value >= beta:
            break

    if best is not None:
        return best

    # no "best" found
    # this means that we have no move available
    # should happen only in case of stalemate/checkmate

    # if the king square is attacked, it's a checkmate
    if board.king_is_in_check(b, b.turn):
        return VALUE_MAX * -1

    # if the king square is not attacked, then it's a stalemate
    return 0
