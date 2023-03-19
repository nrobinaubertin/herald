from . import board, evaluation
from .board import Board
from .constants import COLOR, COLOR_DIRECTION, IS_PIECE, PIECE
from .data_structures import Move
from .evaluation import PIECE_VALUE


def is_futile(b: Board, depth: int, alpha: int, beta: int) -> bool:
    static_eval: int = evaluation.eval_fast(b.squares)

    def futility_margin(depth: int) -> int:
        return 165 * depth

    # colors are inverted since this is a board resulting from our tested move
    if b.turn == COLOR.BLACK:
        if static_eval + futility_margin(depth) <= alpha:
            return True
    else:
        if static_eval - futility_margin(depth) >= beta:
            return True

    return False


# see() returns a colorified score
# if the value is negative, it's good for black, positive it's good for white.
# The value is not exact, it does not represent something else than being positive or negative
# when the returned value is exactly 0, then it's *probably* better not to take
def see(b: Board, target: int, score: int) -> int:
    # return score if it's already in our favor
    # this allows to go faster but see() doesn't return exact results
    if COLOR_DIRECTION[b.turn] * score > 0:
        return score

    # let's use the move that takes the target with the least valuable attacker
    for move in board.capture_moves(b, target):
        # the inversed colorified value of the captured piece
        value = PIECE_VALUE[IS_PIECE[b.squares[target]]] * COLOR_DIRECTION[b.turn]

        # if we capture with a piece that has a lesser value the SEE can only be good
        # so we imagine the capturing piece being taken
        current_score = score + value - PIECE_VALUE[move.moving_piece] * COLOR_DIRECTION[b.turn]
        if COLOR_DIRECTION[b.turn] * current_score > 0:
            return current_score

        # we apply a minmax to the tiny tree of captures to this target square
        if b.turn == COLOR.WHITE:
            return max(score, see(board.push(b, move), target, score + value))
        return min(score, see(board.push(b, move), target, score + value))

    # if no valid move, return score
    return score


def is_bad_capture(b: Board, move: Move) -> bool:
    # a non-capture move is not a bad capture
    if not move.is_capture:
        return False

    if move.moving_piece == PIECE.PAWN or move.captured_piece in [PIECE.KING, PIECE.QUEEN]:
        return False

    # captured piece is worth more than capturing piece
    if (
        PIECE_VALUE[IS_PIECE[b.squares[move.end]]]
        >= PIECE_VALUE[IS_PIECE[b.squares[move.start]]] - 50
    ):
        return False

    # if the piece is defended by a pawn, then it's a bad capture
    for depl in (9, 11) if b.turn == COLOR.WHITE else (-9, -11):
        if (
            IS_PIECE[b.squares[move.start + depl]] == PIECE.PAWN
            and b.squares[move.start + depl] * COLOR_DIRECTION[b.turn] < 0
        ):
            return True

    # if SEE is in favor of the other, then we don't attempt the move
    if see(b, move.end, 0) * COLOR_DIRECTION[b.turn] <= 0:
        return True

    # if we don't know, we have to try the move (we can't say that it's bad for sure)
    return False
