from .constants import COLOR
from typing import Callable, Iterable, List
from .data_structures import Board, Move
from .evaluation import PIECE_VALUE

Move_ordering_fn = Callable[
    [
        Board,
        Iterable[Move],
    ],
    List[Move]
]


def mvv_lva(
    b: Board,
    moves: Iterable[Move],
) -> List[Move]:

    def eval(b, m):
        if m.is_null:
            return 10000
        return (
            int(m.is_capture)
            * (
                1000
                + PIECE_VALUE[abs(b.squares[m.end])] * 1000
                - PIECE_VALUE[abs(b.squares[m.start])]
            ) * b.turn
        )

    moves_evals = [(m, eval(b, m)) for m in moves]

    return [x[0] for x in sorted(
        moves_evals,
        key=lambda x: x[1],
        reverse=b.turn == COLOR.WHITE
    )]


def no_ordering(
    b: Board,
    moves: Iterable[Move],
) -> List[Move]:
    return list(moves)
