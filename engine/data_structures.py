from collections import deque, namedtuple
from engine.evaluation import VALUE_MAX

Move = namedtuple(
    "Move",
    ["start", "end", "is_capture", "is_castle", "en_passant"],
    defaults=[0, 0, False, False, -1],
)

Node = namedtuple(
    "Node",
    ["value", "depth", "pv", "type", "upper", "lower", "squares", "children"],
    defaults=[deque(), None, -VALUE_MAX, VALUE_MAX, None, 0],
)

def toUCI(move: Move) -> str:
    def toNormalNotation(square: int) -> str:
        row = 10 - (square // 10 - 2)
        column = square - (square // 10) * 10
        letter = ({1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g", 8: "h"})[
            column
        ]
        return f"{letter}{row - 2}"

    return f"{toNormalNotation(move.start)}{toNormalNotation(move.end)}"
