from .constants import COLOR, PIECE
from typing import Callable, Iterable, Optional, List
from .data_structures import Board, Move
from .transposition_table import TranspositionTable
from .evaluation import PIECE_VALUE

Move_ordering_fn = Callable[
    [
        Board,
        Iterable[Move],
        Optional[TranspositionTable],
    ],
    List[Move]
]


def is_bad_capture(b: Board, move: Move) -> bool:

    if move.is_null_move:
        return False

    piece_start = b.squares[move.start]

    if abs(piece_start) == PIECE.PAWN:
        return False

    # captured piece is worth more than capturing piece
    if PIECE_VALUE[abs(b.squares[move.end])] >= PIECE_VALUE[abs(b.squares[move.start])]:
        return False

    return True


def mvv_lva(
    b: Board,
    moves: Iterable[Move],
    tt: TranspositionTable | None = None,
) -> List[Move]:

    def eval(b, m):
        if m.is_null_move:
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
    tt: TranspositionTable | None = None,
) -> List[Move]:
    return moves
