from .constants import COLOR
from . import board
from typing import Callable, Iterable
from .data_structures import SmartMove, Board
from .transposition_table import TranspositionTable
from .evaluation import PIECE_VALUE

Move_ordering_fn = Callable[
    [Board, TranspositionTable | None],
    list[SmartMove]
]


def mvv_lva(b: Board, tt: TranspositionTable | None = None) -> Iterable[SmartMove]:
    smart_moves: Iterable[SmartMove] = board.smart_moves(
        b,
        lambda b, m, nb: (
            int(m.is_capture)
            * (
                1000
                + PIECE_VALUE[abs(b.squares[m.end])] * 1000
                - PIECE_VALUE[abs(b.squares[m.start])]
            ) * b.turn
            # + sum(nb.eval, start=1) # there's something wrong in using nb
        )
    )

    return sorted(
        smart_moves,
        key=lambda x: x.eval,
        reverse=b.turn == COLOR.WHITE
    )
