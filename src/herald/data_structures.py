from collections import deque, namedtuple
from typing import Iterable

from .constants import PIECE, VALUE_MAX

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
