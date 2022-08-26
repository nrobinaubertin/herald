from collections import deque, namedtuple
from .constants import PIECE, VALUE_MAX

Move = namedtuple("Move", [
       "start",
       "end",
       "moving_piece",
       "is_capture",
       "is_castle",
       "en_passant",
       "is_king_capture"
    ],
    defaults=[0, False, False, -1, False],
)

Node = namedtuple(
    "Node",
    ["value", "depth", "pv", "type", "upper", "lower", "squares", "children"],
    defaults=[deque(), None, -VALUE_MAX, VALUE_MAX, None, 0],
)

SmartMove = namedtuple("SmartMove", [
        "move",
        "board",
        "eval",
    ]
)

Board = namedtuple("Board", [
        # array of PIECE * COLOR
        # 120 squares for a 10*12 mailbox
        # https://www.chessprogramming.org/Mailbox
        "squares",
        # move history
        "moves_history",
        # color of the player whos turn it is
        "turn",
        # array reprensenting castling rights
        "castling_rights",
        # the following values are ints with default values
        "en_passant",
        "half_move",
        "full_move",
        "king_en_passant",
        "value",
    ],
    defaults=[-1, 0, 0, -1, 0]
)


Search = namedtuple("Search", [
        "move",
        "depth",
        "score",
        "nodes",
        "time",
        "best_node",
        "pv",
        "stop_search",
    ],
    defaults=[False]
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
