from .constants import COLOR, PIECE
from .data_structures import Board, Move
from .evaluation import PIECE_VALUE
from . import board


def is_futile_move(b: Board, move: Move) -> bool:
    if is_bad_capture(b, move):
        return True

    piece_start = b.squares[move.start]

    # we don't test bishops in corners
    if (
        abs(piece_start) == PIECE.BISHOP
        and move.end in [21, 28, 91, 98]
    ):
        return True

    # we don't want a knight on the edge
    if (
        abs(piece_start) == PIECE.KNIGHT
        and (
            move.end % 10 in [2, 9]
            or move.end // 10 in [1, 8]
        )
    ):
        return True

    return False


def see(b: Board, target: int, score: int) -> int:

    # return score if it's already in our favor
    # this allows to go faster but see() doesn't return exact results
    if b.turn * score > 0:
        return score

    # let's use the move that takes the target with
    # the least valuable attacker
    for move in filter(lambda x: x.end == target, board.pseudo_legal_moves(b, True)):
        value = PIECE_VALUE[abs(b.squares[target])] * b.turn

        if score != 0:
            if b.turn == COLOR.WHITE:
                return max(score, see(board.push(b, move), target, score + value))
            return min(score, see(board.push(b, move), target, score + value))
        return see(board.push(b, move), target, score + value)

    return score


def is_bad_capture(b: Board, move: Move) -> bool:

    # a non-capture move is not a bad capture
    if not move.is_capture:
        return False

    piece_start = b.squares[move.start]

    if abs(piece_start) == PIECE.PAWN or abs(piece_start) == PIECE.KING:
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

    # if SEE is negative, then we don't attempt the move
    if see(b, move.end, 0) * b.turn < 0:
        return True

    # if we don't know, we have to try the move (we can't say that it's bad)
    return False
