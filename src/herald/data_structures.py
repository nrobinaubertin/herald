from array import array
from collections import deque, namedtuple
from enum import IntEnum
from typing import Iterable

from .constants import PIECE, VALUE_MAX


class MoveType(IntEnum):
    UNKNOWN = 0
    INVALID = 1
    PSEUDO_LEGAL = 2
    LEGAL = 3
    QUIESCENT = 4
    NULL = 5


Move = namedtuple(
    "Move",
    [
        "start",
        "end",
        "moving_piece",
        "captured_piece",
        "is_capture",
        "is_castle",
        "en_passant",
        "is_king_capture",
        "is_quiescent",
    ],
    defaults=[0, 0, False, False, -1, False, False, False],
)

Node = namedtuple(
    "Node",
    ["value", "depth", "pv", "type", "upper", "lower", "squares", "children", "full_move"],
    defaults=[deque(), None, -VALUE_MAX, VALUE_MAX, None, 0, 0],
)


Board = namedtuple(
    "Board",
    [
        # array of PIECE * COLOR
        # 120 squares for a 10*12 mailbox
        # https://www.chessprogramming.org/Mailbox
        "squares",
        # color of the player who's turn it is
        "turn",
        # positions history to check for repetition
        "positions_history",
        # array reprensenting castling rights (index CASTLE + COLOR)
        "castling_rights",
        # the following values are ints with default values
        "en_passant",
        "half_move",
        "full_move",
        "king_en_passant",
        "pawn_number",
        "pawn_in_file",
    ],
    defaults=[-1, 0, 0, array("b"), array("b"), array("b")],
)


Search = namedtuple(
    "Search",
    [
        "move",
        "depth",
        "score",
        "nodes",
        "time",
        "pv",
        "stop_search",
    ],
    defaults=[False],
)


def decompose_square(square: int) -> tuple[int, int]:
    row = 10 - (square // 10 - 2) - 2
    column = square - (square // 10) * 10
    return (row, column)


def to_square_notation(uci: str) -> int:
    uci = uci.lower()
    digits = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}
    return digits[uci[0]] + (10 - int(uci[1])) * 10


def to_normal_notation(square: int) -> str:
    row, column = decompose_square(square)
    letter = ({1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g", 8: "h"})[column]
    return f"{letter}{row}"


def is_promotion(move: Move) -> bool:
    row, _ = decompose_square(move.end)
    return move.moving_piece == PIECE.PAWN and (row in (8, 1))


def to_uci(input_move: Move | Iterable[Move]) -> str:
    if isinstance(input_move, Move):
        return (
            f"{to_normal_notation(input_move.start)}"
            f"{to_normal_notation(input_move.end)}"
            f"{'q' if is_promotion(input_move) else ''}"
            f"{'*' if input_move.is_quiescent else ''}"
        )

    if isinstance(input_move, Iterable):
        return ",".join([to_uci(x) for x in input_move])

    raise Exception("Unknown input_move for to_uci()")
