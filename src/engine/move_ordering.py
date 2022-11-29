from .constants import COLOR
from . import board
from typing import Callable, Iterable
from .data_structures import Board, Move
from .transposition_table import TranspositionTable
from .evaluation import PIECE_VALUE

Move_ordering_fn = Callable[
    [Board, TranspositionTable | None],
    list[Move]
]


def mvv_lva(b: Board, tt: TranspositionTable | None = None) -> Iterable[Move]:
    pseudo_legal_moves: Iterable[Move] = board.pseudo_legal_moves(b)

    def eval(b, m):
        return (
            int(m.is_capture)
            * (
                1000
                + PIECE_VALUE[abs(b.squares[m.end])] * 1000
                - PIECE_VALUE[abs(b.squares[m.start])]
            ) * b.turn
        )

    moves_evals = [(m, eval(b, m)) for m in pseudo_legal_moves]

    return [x[0] for x in sorted(
        moves_evals,
        key=lambda x: x[1],
        reverse=b.turn == COLOR.WHITE
    )]
