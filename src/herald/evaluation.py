from functools import cache
from typing import Callable

from .board import Board
from .constants import COLOR, COLOR_DIRECTION, IS_PIECE, PIECE, get_color

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

START_MATERIAL = (
    PIECE_VALUE[PIECE.KING] * 2
    + PIECE_VALUE[PIECE.QUEEN] * 2
    + PIECE_VALUE[PIECE.ROOK] * 4
    + PIECE_VALUE[PIECE.BISHOP] * 4
    + PIECE_VALUE[PIECE.KNIGHT] * 4
    + PIECE_VALUE[PIECE.PAWN] * 16
)

# fmt: off
PIECE_SQUARE_TABLE = [
    {
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
    },
    {
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
            -50, 0, 0, 0, 0, 0, 0, -50,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 10, 10, 10, 10, 0, 0,
            0, 0, 10, 10, 10, 10, 0, 0,
            0, 0, 10, 10, 10, 10, 0, 0,
            0, 0, 10, 10, 10, 10, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            -50, 0, 0, 0, 0, 0, 0, -50,
        ),
        PIECE.ROOK: (
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
        ),
        PIECE.QUEEN: (
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 20, 20, 20, 20, 0, 0,
            0, 0, 20, 20, 20, 20, 0, 0,
            0, 0, 20, 20, 20, 20, 0, 0,
            0, 0, 20, 20, 20, 20, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
        ),
        PIECE.KING: (
            -10, -10, -10, -10, -10, -10, -10, -10,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, 0, 10, 10, 10, 10, 0, -10,
            -10, 0, 10, 10, 10, 10, 0, -10,
            -10, 0, 10, 10, 10, 10, 0, -10,
            -10, 0, 10, 10, 10, 10, 0, -10,
            -10, 0, 0, 0, 0, 0, 0, -10,
            -10, -10, -10, -10, -10, -10, -10, -10,
        ),
    },
]
# fmt: on

# arrange pst to match our mailbox
PIECE_SQUARE_TABLE_MAILBOX = []
for table in PIECE_SQUARE_TABLE:
    new_piece_table: dict[PIECE, list[int]] = {}
    for piece in table:
        new_table = []
        for i in range(20):
            new_table.append(0)
        for i in range(8):
            new_table.append(0)  # first column of the mailbox
            for j in range(8):
                new_table.append(table[piece][i * 8 + j])
            new_table.append(0)  # last column of the mailbox
        for i in range(20):
            new_table.append(0)
        new_piece_table[piece] = new_table
    PIECE_SQUARE_TABLE_MAILBOX.append(new_piece_table)

Eval_fn = Callable[
    [
        Board,
    ],
    int,
]


@cache
def remaining_material(squares: tuple[int]) -> int:
    material = 0
    for i in range(8):
        for j in range(8):
            square = (2 + j) * 10 + (i + 1)
            piece = squares[square]
            if piece == PIECE.EMPTY:
                continue
            assert 0 < IS_PIECE[piece] < 7
            material += PIECE_VALUE[IS_PIECE[piece]]
    return material


@cache
def remaining_material_percent(squares: tuple[int]) -> float:
    return (remaining_material(squares) - PIECE_VALUE[PIECE.KING] * 2) / (
        START_MATERIAL - PIECE_VALUE[PIECE.KING] * 2
    )


# only material
def eval_simple(b: Board) -> int:
    evaluation = 0
    for i in range(8):
        for j in range(8):
            square = (2 + j) * 10 + (i + 1)
            piece = b.squares[square]
            if piece == PIECE.EMPTY:
                continue
            assert 0 < IS_PIECE[piece] < 7
            if get_color(piece) == COLOR.WHITE:
                evaluation += PIECE_VALUE[IS_PIECE[piece]]
            else:
                evaluation -= PIECE_VALUE[IS_PIECE[piece]]
    return evaluation


# adjustments of piece value based on the number of own pawns
# fmt: off
PIECE_ADJUSTEMENTS_OWN_PAWN_NUMBER = {
    PIECE.EMPTY: (0, 0, 0, 0, 0, 0, 0, 0, 0),
    PIECE.PAWN: (0, 0, 0, 0, 0, 0, 0, 0, 0),
    PIECE.KNIGHT: (-20, -16, -12, -8, -4, 0, 4, 8, 12),
    PIECE.BISHOP: (0, 0, 0, 0, 0, 0, 0, 0, 0),
    PIECE.ROOK: (15, 12, 9, 6, 3, 0, -3, -6, -9),
    PIECE.QUEEN: (0, 0, 0, 0, 0, 0, 0, 0, 0),
    PIECE.KING: (0, 0, 0, 0, 0, 0, 0, 0, 0),
}
# fmt: on

DOUBLED_PAWN_PENALTY = -20

# Bonus for rook on semiopen/open file
ROOK_ON_FILE = [21, 26]

# PassedRank[Rank] contains a bonus according to the rank of a passed pawn
PASSED_RANK = [0, 0, 0, 0, 10, 17, 15, 62, 168, 276, 0, 0]


def eval_new(b: Board) -> int:
    evaluation = 0

    for i in range(8):
        for j in range(8):
            square = (2 + j) * 10 + (i + 1)
            piece = b.squares[square]
            if piece == PIECE.EMPTY:
                continue
            x = i + 1
            y = 2 + j
            color = get_color(piece)

            eval_curr = 0
            eval_curr += PIECE_VALUE[IS_PIECE[piece]]

            assert 0 < IS_PIECE[piece] < 7
            assert 0 <= b.pawn_number[color] <= 8

            if color == COLOR.WHITE:
                eval_curr += int(
                    PIECE_SQUARE_TABLE_MAILBOX[0][IS_PIECE[piece]][square] * remaining_material_percent(b.squares)
                    + PIECE_SQUARE_TABLE_MAILBOX[1][IS_PIECE[piece]][square] * (1 - remaining_material_percent(b.squares))
                )
            else:
                eval_curr += int(
                    PIECE_SQUARE_TABLE_MAILBOX[0][IS_PIECE[piece]][119 - square] * remaining_material_percent(b.squares)
                    + PIECE_SQUARE_TABLE_MAILBOX[1][IS_PIECE[piece]][119 - square] * (1 - remaining_material_percent(b.squares))
                )

            eval_curr += PIECE_ADJUSTEMENTS_OWN_PAWN_NUMBER[IS_PIECE[piece]][b.pawn_number[color]]
            pawn_file: int = x + 10 * color
            opposite_pawn_file: int = x + 10 * (color * -1)
            if IS_PIECE[piece] == PIECE.PAWN:
                if b.pawn_in_file[pawn_file] > 0:
                    eval_curr += DOUBLED_PAWN_PENALTY
                    if b.pawn_in_file[pawn_file] > 1:
                        eval_curr += DOUBLED_PAWN_PENALTY
                else:
                    if (
                        b.pawn_in_file[opposite_pawn_file + 1] == 0
                        and b.pawn_in_file[opposite_pawn_file - 1] == 0
                    ):
                        # bonus for passed pawn
                        if color == COLOR.WHITE:
                            eval_curr += PASSED_RANK[11 - y]
                        else:
                            eval_curr += PASSED_RANK[y]
            if IS_PIECE[piece] == PIECE.ROOK:
                if b.pawn_in_file[pawn_file] == 0:
                    eval_curr += ROOK_ON_FILE[0]
                    if b.pawn_in_file[opposite_pawn_file] == 0:
                        eval_curr += ROOK_ON_FILE[1]
            if IS_PIECE[piece] == PIECE.KING:
                # we like having pawns in front of our king
                for depl in [
                    -10 * COLOR_DIRECTION[color],
                    -10 * COLOR_DIRECTION[color] + 1,
                    -10 * COLOR_DIRECTION[color] - 1,
                ]:
                    if (
                        IS_PIECE[b.squares[square + depl]] == PIECE.PAWN
                        and b.squares[square + depl] * color > 0
                    ):
                        eval_curr += 20

            if color == COLOR.WHITE:
                evaluation += eval_curr
            else:
                evaluation -= eval_curr

    return evaluation
