from collections import deque, namedtuple
from engine.evaluation import VALUE_MAX
from engine.constants import PIECE

Move = namedtuple(
    "Move",
    ["start", "end", "moving_piece", "is_capture", "is_castle", "en_passant"],
    defaults=[0, 0, False, False, -1],
)

Node = namedtuple(
    "Node",
    ["value", "depth", "pv", "type", "upper", "lower", "squares", "children"],
    defaults=[deque(), None, -VALUE_MAX, VALUE_MAX, None, 0],
)


def decompose_square(square: int):
    row = 10 - (square // 10 - 2) - 2
    column = square - (square // 10) * 10
    return (row, column)


def to_normal_notation(square: int) -> str:
    row, column = decompose_square(square)
    letter = ({1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g", 8: "h"})[column]
    return f"{letter}{row}"


def is_promotion(move: Move) -> bool:
    row, _ = decompose_square(move.end)
    return abs(move.moving_piece) == PIECE.PAWN and (row in (8, 1))


def to_uci(move: Move) -> str:
    return f"{to_normal_notation(move.start)}{to_normal_notation(move.end)}{'q' if is_promotion(move) else ''}"
