from enum import IntEnum


class CASTLE(IntEnum):
    KING_SIDE = 1
    QUEEN_SIDE = 2


class COLOR(IntEnum):
    WHITE = 1
    BLACK = -1


COLOR_IDX = {COLOR.WHITE: 0, COLOR.BLACK: 1}


class PIECE(IntEnum):
    EMPTY = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6
    INVALID = 7


IS_PIECE = {
    -7: PIECE.INVALID,
    -6: PIECE.KING,
    -5: PIECE.QUEEN,
    -4: PIECE.ROOK,
    -3: PIECE.BISHOP,
    -2: PIECE.KNIGHT,
    -1: PIECE.PAWN,
    0: PIECE.EMPTY,
    1: PIECE.PAWN,
    2: PIECE.KNIGHT,
    3: PIECE.BISHOP,
    4: PIECE.ROOK,
    5: PIECE.QUEEN,
    6: PIECE.KING,
    7: PIECE.INVALID,
}


ASCII_REP: dict[int, str] = {
    0: ".",
    (PIECE.PAWN * COLOR.WHITE): "P",
    (PIECE.KNIGHT * COLOR.WHITE): "N",
    (PIECE.BISHOP * COLOR.WHITE): "B",
    (PIECE.ROOK * COLOR.WHITE): "R",
    (PIECE.QUEEN * COLOR.WHITE): "Q",
    (PIECE.KING * COLOR.WHITE): "K",
    (PIECE.PAWN * COLOR.BLACK): "p",
    (PIECE.KNIGHT * COLOR.BLACK): "n",
    (PIECE.BISHOP * COLOR.BLACK): "b",
    (PIECE.ROOK * COLOR.BLACK): "r",
    (PIECE.QUEEN * COLOR.BLACK): "q",
    (PIECE.KING * COLOR.BLACK): "k",
}

VALUE_MAX: int = 12_000


def get_color(value: int):
    if value >= 0:
        return 1
    return -1
