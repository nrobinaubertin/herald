from . import board
from .board import Board
from .constants import COLOR, PIECE
from .data_structures import Move
from .evaluation import PIECE_VALUE


def see(b: Board, target: int, score: int) -> int:

    # return score if it's already in our favor
    # this allows to go faster but see() doesn't return exact results
    if b.turn * score > 0:
        return score

    # let's use the move that takes the target with
    # the least valuable attacker
    # for move in filter(lambda x: x.end == target, board.pseudo_legal_moves(b, True)):
    for move in board.capture_moves(b, target):
        value = PIECE_VALUE[PIECE(abs(b.squares[target]))] * b.turn

        if score != 0:
            if b.turn == COLOR.WHITE:
                return max(score, see(board.push(b, move), target, score + value))
            return min(score, see(board.push(b, move), target, score + value))
        return see(board.push(b, move), target, score + value)

    return score


def is_bad_capture(b: Board, move: Move, with_see: bool = True) -> bool:

    # a non-capture move is not a bad capture
    if not move.is_capture:
        return False

    if move.moving_piece == PIECE.PAWN or move.captured_piece in [PIECE.KING, PIECE.QUEEN]:
        return False

    # captured piece is worth more than capturing piece
    if PIECE_VALUE[abs(b.squares[move.end])] >= PIECE_VALUE[abs(b.squares[move.start])] - 50:
        return False

    # if the piece is defended by a pawn, then it's a bad capture
    for depl in [9, 11] if b.turn == COLOR.WHITE else [-9, -11]:
        if (
            abs(b.squares[move.start + depl]) == PIECE.PAWN
            and b.squares[move.start + depl] * b.turn < 0
        ):
            return True

    if with_see:
        # if SEE is negative, then we don't attempt the move
        if see(b, move.end, 0) * b.turn < 0:
            return True

    # if we don't know, we have to try the move (we can't say that it's bad)
    return False
