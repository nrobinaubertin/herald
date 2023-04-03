from functools import cache

from .constants import COLOR, IS_PIECE, PIECE, get_color

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
            -50, 0, 0, 0, 0, 0, 0, -50,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 10, 10, 10, 10, 0, 0,
            0, 0, 10, 10, 10, 10, 0, 0,
            0, 0, 10, 10, 10, 10, 0, 0,
            0, 0, 10, 10, 10, 10, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            -50, 0, 0, 0, 0, 0, 0, -50,
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
            -20, 0, 0, 0, 0, 0, 0, -20,
            0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 20, 20, 20, 20, 0, 0,
            0, 0, 20, 20, 20, 20, 0, 0,
            0, 0, 20, 20, 20, 20, 0, 0,
            0, 0, 20, 20, 20, 20, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0,
            -20, 0, 0, 0, 0, 0, 0, -20,
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
def remaining_material_percent(remaining_material: int) -> float:
    return float(
        (remaining_material - PIECE_VALUE[PIECE.KING] * 2)
        / (START_MATERIAL - PIECE_VALUE[PIECE.KING] * 2)
    )


@cache
def eval_fast(squares: tuple[int], remaining_material: int) -> int:
    evaluation = 0

    for i in range(8):
        for j in range(8):
            square = (2 + j) * 10 + (i + 1)
            piece = squares[square]
            if piece == PIECE.EMPTY:
                continue
            color = get_color(piece)

            assert 0 < IS_PIECE[piece] < 7

            if color == COLOR.WHITE:
                evaluation += PIECE_VALUE[IS_PIECE[piece]]
                evaluation += int(
                    PIECE_SQUARE_TABLE_MAILBOX[0][IS_PIECE[piece]][square]
                    * remaining_material_percent(remaining_material)
                    + PIECE_SQUARE_TABLE_MAILBOX[1][IS_PIECE[piece]][square]
                    * (1 - remaining_material_percent(remaining_material))
                )
            else:
                invsquare = (9 - j) * 10 + (i + 1)
                evaluation -= PIECE_VALUE[IS_PIECE[piece]]
                evaluation -= int(
                    PIECE_SQUARE_TABLE_MAILBOX[0][IS_PIECE[piece]][invsquare]
                    * remaining_material_percent(remaining_material)
                    + PIECE_SQUARE_TABLE_MAILBOX[1][IS_PIECE[piece]][invsquare]
                    * (1 - remaining_material_percent(remaining_material))
                )
    return evaluation
