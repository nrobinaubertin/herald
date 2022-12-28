from array import array
from . import board
from .constants import PIECE, COLOR
from .data_structures import Board
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


Eval_fn = Callable[
    [
        Board,
    ],
    int
]


# only material
def eval_simple(b: Board) -> int:
    evaluation = 0
    for square in board.pieces(b):
        piece = b.squares[square]
        color = abs(piece) // piece
        evaluation += PIECE_VALUE[abs(piece)] * color
    return evaluation


# material + pst
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
                PIECE_SQUARE_TABLE_MAILBOX[abs(piece)][119 - square] * color
            )
    return evaluation


# adjustements of piece value based on the number of own pawns
PIECE_ADJUSTEMENTS_OWN_PAWN_NUMBER = {
    PIECE.EMPTY: (0, 0, 0, 0, 0, 0, 0, 0, 0),
    PIECE.PAWN: (0, 0, 0, 0, 0, 0, 0, 0, 0),
    PIECE.KNIGHT: (-20, -16, -12, -8, -4, 0, 4, 8, 12),
    PIECE.BISHOP: (0, 0, 0, 0, 0, 0, 0, 0, 0),
    PIECE.ROOK: (15, 12, 9, 6, 3, 0, -3, -6, -9),
    PIECE.QUEEN: (0, 0, 0, 0, 0, 0, 0, 0, 0),
    PIECE.KING: (0, 0, 0, 0, 0, 0, 0, 0, 0),
}

DOUBLED_PAWN_PENALTY = -20

# Bonus for rook on semiopen/open file
ROOK_ON_FILE = [21, 26]

# PassedRank[Rank] contains a bonus according to the rank of a passed pawn
PASSED_RANK = [0, 0, 0, 0, 10, 17, 15, 62, 168, 276, 0, 0]


def eval_new(b: Board) -> int:

    evaluation = 0

    pawn_number = {
        COLOR.WHITE: 0,
        COLOR.BLACK: 0,
    }

    pawn_in_file = [{COLOR.WHITE: 0, COLOR.BLACK: 0}] * 10

    # first pass to count pawns
    for i in range(8):
        for j in range(8):
            square = (2 + j) * 10 + (i + 1)
            piece = b.squares[square]
            if piece == 0 or piece == 7:
                continue
            if abs(piece) == PIECE.PAWN:
                color = abs(piece) // piece
                pawn_number[color] += 1
                pawn_in_file[i][color] += 1

    for i in range(8):
        for j in range(8):
            square = (2 + j) * 10 + (i + 1)
            x = i + 1
            y = 2 + j
            piece = b.squares[square]
            if piece == 0 or piece == 7:
                continue
            color = abs(piece) // piece
            evaluation += PIECE_VALUE[abs(piece)] * color
            evaluation += PIECE_ADJUSTEMENTS_OWN_PAWN_NUMBER[abs(piece)][pawn_number[color]]
            if color == COLOR.WHITE:
                evaluation += PIECE_SQUARE_TABLE_MAILBOX[abs(piece)][square] * color
            else:
                evaluation += (
                    PIECE_SQUARE_TABLE_MAILBOX[abs(piece)][119 - square] * color
                )
            if abs(piece) == PIECE.PAWN and pawn_in_file[x][color] > 0:
                evaluation += DOUBLED_PAWN_PENALTY * color
                if pawn_in_file[x][color] > 1:
                    evaluation += DOUBLED_PAWN_PENALTY * color
            if (
                abs(piece) == PIECE.PAWN
                and pawn_in_file[x][color * -1] == 0
                and pawn_in_file[x + 1][color * -1] == 0
                and pawn_in_file[x - 1][color * -1] == 0
            ):
                # bonus for passed pawn
                if color == COLOR.WHITE:
                    evaluation += PASSED_RANK[11 - y] * color
                else:
                    evaluation += PASSED_RANK[y] * color
            if abs(piece) == PIECE.ROOK:
                if pawn_in_file[x][color] == 0:
                    evaluation += ROOK_ON_FILE[0] * color
                    if pawn_in_file[x][color * -1] == 0:
                        evaluation += ROOK_ON_FILE[1] * color
            if abs(piece) == PIECE.KING:
                # we like having pawns in front of our king
                for depl in [10 * color, 10 * color + 1, 10 * color - 1]:
                    if (
                        abs(b.squares[square + depl]) == PIECE.PAWN
                        and b.squares[square + depl] * color > 0
                    ):
                        evaluation += 20 * color
                for depl in [20 * color, 20 * color + 1, 20 * color - 1]:
                    if (
                        abs(b.squares[square + depl]) == PIECE.PAWN
                        and b.squares[square + depl] * color > 0
                    ):
                        evaluation += 5 * color

    return evaluation
