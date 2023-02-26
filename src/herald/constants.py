from functools import cache
from enum import IntEnum


class CASTLE(IntEnum):
    KING_SIDE = 0
    QUEEN_SIDE = 1


class COLOR(IntEnum):
    WHITE = 0
    BLACK = 1
    UNKNOWN = 99


COLOR_DIRECTION = {COLOR.BLACK: -1, COLOR.WHITE: 1}


INV_COLOR = {
    COLOR.WHITE: COLOR.BLACK,
    COLOR.BLACK: COLOR.WHITE,
}


class PIECE(IntEnum):
    EMPTY = 0
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6
    INVALID = 99


IS_PIECE = {
    0: PIECE.EMPTY,
    1: PIECE.PAWN,
    2: PIECE.KNIGHT,
    3: PIECE.BISHOP,
    4: PIECE.ROOK,
    5: PIECE.QUEEN,
    6: PIECE.KING,
    7: PIECE.PAWN,
    8: PIECE.KNIGHT,
    9: PIECE.BISHOP,
    10: PIECE.ROOK,
    11: PIECE.QUEEN,
    12: PIECE.KING,
    99: PIECE.INVALID,
}


IS_PVALUE = {
    (COLOR.WHITE, PIECE.PAWN): 1,
    (COLOR.WHITE, PIECE.KNIGHT): 2,
    (COLOR.WHITE, PIECE.BISHOP): 3,
    (COLOR.WHITE, PIECE.ROOK): 4,
    (COLOR.WHITE, PIECE.QUEEN): 5,
    (COLOR.WHITE, PIECE.KING): 6,
    (COLOR.BLACK, PIECE.PAWN): 7,
    (COLOR.BLACK, PIECE.KNIGHT): 8,
    (COLOR.BLACK, PIECE.BISHOP): 9,
    (COLOR.BLACK, PIECE.ROOK): 10,
    (COLOR.BLACK, PIECE.QUEEN): 11,
    (COLOR.BLACK, PIECE.KING): 12,
}


ASCII_REP: dict[int, str] = {
    0: ".",
    1: "P",
    2: "N",
    3: "B",
    4: "R",
    5: "Q",
    6: "K",
    7: "p",
    8: "n",
    9: "b",
    10: "r",
    11: "q",
    12: "k",
    99: "-",
}

VALUE_MAX: int = 12_000


@cache
def get_color(square: int) -> COLOR:
    if 0 < square < 7:
        return COLOR.WHITE
    if 6 < square < 13:
        return COLOR.BLACK
    return COLOR.UNKNOWN
