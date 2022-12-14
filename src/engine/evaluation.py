from array import array
from . import board
from .constants import PIECE, COLOR
from .data_structures import Move, Board
from .transposition_table import TranspositionTable
from typing import Callable

PIECE_VALUE = {
    PIECE.EMPTY: 0,
    PIECE.PAWN: 100,
    PIECE.KNIGHT: 280,
    PIECE.BISHOP: 320,
    PIECE.ROOK: 479,
    PIECE.QUEEN: 929,
}

# The king has more value than all the other pieces combined
PIECE_VALUE[PIECE.KING] = (
    PIECE_VALUE[PIECE.QUEEN] * 9
    + PIECE_VALUE[PIECE.KNIGHT] * 2
    + PIECE_VALUE[PIECE.BISHOP] * 2
    + PIECE_VALUE[PIECE.ROOK] * 2
)

PIECE_SQUARE_TABLE = {
    PIECE.PAWN: (
        0, 0, 0, 0, 0, 0, 0, 0,
        78, 83, 86, 73, 102, 82, 85, 90,
        7, 29, 21, 44, 40, 31, 44, 7,
        -17, 16, -2, 15, 14, 0, 15, -13,
        -26, 3, 10, 9, 6, 1, 0, -23,
        -22, 9, 5, -11, -10, -2, 3, -19,
        -31, 8, -7, -37, -36, -14, 3, -31,
        0, 0, 0, 0, 0, 0, 0, 0,
    ),
    PIECE.KNIGHT: (
        -66, -53, -75, -75, -10, -55, -58, -70,
        -3, -6, 100, -36, 4, 62, -4, -14,
        10, 67, 1, 74, 73, 27, 62, -2,
        24, 24, 45, 37, 33, 41, 25, 17,
        -1, 5, 31, 21, 22, 35, 2, 0,
        -18, 10, 13, 22, 18, 15, 11, -14,
        -23, -15, 2, 0, 2, 0, -23, -20,
        -74, -23, -26, -24, -19, -35, -22, -69,
    ),
    PIECE.BISHOP: (
        -59, -78, -82, -76, -23, -107, -37, -50,
        -11, 20, 35, -42, -39, 31, 2, -22,
        -9, 39, -32, 41, 52, -10, 28, -14,
        25, 17, 20, 34, 26, 25, 15, 10,
        13, 10, 17, 23, 17, 16, 0, 7,
        14, 25, 24, 15, 8, 25, 20, 15,
        19, 20, 11, 6, 7, 6, 20, 16,
        -7, 2, -15, -12, -14, -15, -10, -10,
    ),
    PIECE.ROOK: (
        35, 29, 33, 4, 37, 33, 56, 50,
        55, 29, 56, 67, 55, 62, 34, 60,
        19, 35, 28, 33, 45, 27, 25, 15,
        0, 5, 16, 13, 18, -4, -9, -6,
        -28, -35, -16, -21, -13, -29, -46, -30,
        -42, -28, -42, -25, -25, -35, -26, -46,
        -53, -38, -31, -26, -29, -43, -44, -53,
        -30, -24, -18, 5, -2, -18, -31, -32,
    ),
    PIECE.QUEEN: (
        6, 1, -8, -104, 69, 24, 88, 26,
        14, 32, 60, -10, 20, 76, 57, 24,
        -2, 43, 32, 60, 72, 63, 43, 2,
        1, -16, 22, 17, 25, 20, -13, -6,
        -14, -15, -2, -5, -1, -10, -20, -22,
        -30, -6, -13, -11, -16, -11, -16, -27,
        -36, -18, 0, -19, -15, -15, -21, -38,
        -39, -30, -31, -13, -31, -36, -34, -42,
    ),
    PIECE.KING: (
        4, 54, 47, -99, -99, 60, 83, -62,
        -32, 10, 55, 56, 56, 55, 10, 3,
        -62, 12, -57, 44, -67, 28, 37, -31,
        -55, 50, 11, -4, -19, 13, 0, -49,
        -55, -43, -52, -28, -51, -47, -8, -50,
        -47, -42, -43, -79, -64, -32, -29, -32,
        -4, 3, -14, -50, -57, -18, 13, 4,
        17, 30, -3, -14, 6, -1, 40, 18,
    ),
}

# arrange pst to match our mailbox
PIECE_SQUARE_TABLE_MAILBOX = {
    PIECE.PAWN: array('b'),
    PIECE.KNIGHT: array('b'),
    PIECE.BISHOP: array('b'),
    PIECE.ROOK: array('b'),
    PIECE.QUEEN: array('b'),
    PIECE.KING: array('b'),
}

# Initialize PIECE_SQUARE_TABLE_MAILBOX
for piece in PIECE_SQUARE_TABLE:
    new_table = array("b")
    for i in range(20):
        new_table.append(0)
    for i in range(8):
        new_table.append(0)  # first column of the mailbox
        for j in range(8):
            new_table.append(PIECE_SQUARE_TABLE[piece][i * 8 + j])
        new_table.append(0)  # last column of the mailbox
    for i in range(20):
        new_table.append(0)
    PIECE_SQUARE_TABLE_MAILBOX[piece] = new_table


# return change in PST evaluation pre-move
def eval_pst_inc_pre(squares, move: Move) -> int:
    value = 0

    piece_start = squares[move.start]
    assert piece_start != 0, "Moving piece cannot be empty"
    assert abs(piece_start) != 7, "Moving piece cannot be invalid"
    color_start = abs(piece_start) // piece_start
    assert color_start != 0, "Color of moving piece should not be empty"

    value -= PIECE_VALUE[abs(piece_start)] * color_start
    if color_start == COLOR.WHITE:
        value -= PIECE_SQUARE_TABLE_MAILBOX[abs(piece_start)][move.start] * color_start
    else:
        value -= PIECE_SQUARE_TABLE_MAILBOX[abs(piece_start)][120 - move.start] * color_start

    # simple capture move
    piece_end = squares[move.end]
    if piece_end != 0:
        color_end = abs(piece_end) // piece_end
        value -= PIECE_VALUE[abs(piece_end)] * color_end
        if color_end == COLOR.WHITE:
            value -= PIECE_SQUARE_TABLE_MAILBOX[abs(piece_end)][move.end] * color_end
        else:
            value -= PIECE_SQUARE_TABLE_MAILBOX[abs(piece_end)][120 - move.end] * color_end

    return value


# special function used for en_passant score changes
def eval_pst_inc_en_passant(squares, target) -> int:
    en_passant_score_change = 0
    piece_target = squares[target]
    color_target = abs(piece_target) // piece_target

    en_passant_score_change -= PIECE_VALUE[abs(piece_target)] * color_target
    if color_target == COLOR.WHITE:
        en_passant_score_change -= PIECE_SQUARE_TABLE_MAILBOX[abs(piece_target)][target] * color_target
    else:
        en_passant_score_change -= PIECE_SQUARE_TABLE_MAILBOX[abs(piece_target)][120 - target] * color_target
    return en_passant_score_change


# return change in PST evaluation pre-move
def eval_pst_inc_post(squares, move: Move) -> int:
    value = 0

    piece_end = squares[move.end]
    assert piece_end != 0, "Moving piece cannot be empty"
    assert abs(piece_end) != 7, "Moving piece cannot be invalid"
    color_end = abs(piece_end) // piece_end
    assert color_end != 0, "Color of moving piece should not be empty"

    value += PIECE_VALUE[abs(piece_end)] * color_end
    if color_end == COLOR.WHITE:
        value += PIECE_SQUARE_TABLE_MAILBOX[abs(piece_end)][move.end] * color_end
    else:
        value += PIECE_SQUARE_TABLE_MAILBOX[abs(piece_end)][120 - move.end] * color_end

    return value


Eval_fn = Callable[
    [
        Board,
        TranspositionTable | None,
    ],
    int
]


# full board PST evaluation
def eval_pst(b: Board) -> int:
    evaluation = 0
    for square in board.pieces(b):
        piece = b.squares[square]
        color = abs(piece) // piece
        evaluation += PIECE_VALUE[abs(piece)] * color
        if color == COLOR.WHITE:
            evaluation += PIECE_SQUARE_TABLE_MAILBOX[abs(piece)][square] * color
        else:
            evaluation += (
                PIECE_SQUARE_TABLE_MAILBOX[abs(piece)][120 - square] * color
            )
    return evaluation


def eval_simple(
    b: Board,
    transposition_table: TranspositionTable | None = None,
) -> int:
    return sum(b.eval, start=1)
