from .constants import COLOR
from . import board
from typing import Callable, Iterable
from .data_structures import Board, Move, MoveType
from .transposition_table import TranspositionTable
from .evaluation import PIECE_VALUE

Move_ordering_fn = Callable[
    [
        Board,
        TranspositionTable | None,
        MoveType,
    ],
    list[Move]
]


def mvv_lva(
    b: Board,
    tt: TranspositionTable | None = None,
    move_type: MoveType = MoveType.PSEUDO_LEGAL,
) -> Iterable[Move]:

    moves = []
    if move_type == MoveType.PSEUDO_LEGAL:
        moves: Iterable[Move] = board.pseudo_legal_moves(b)
    if move_type == MoveType.LEGAL:
        moves: Iterable[Move] = board.legal_moves(b)

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
    tt: TranspositionTable | None = None,
    move_type=MoveType.PSEUDO_LEGAL,
) -> Iterable[Move]:

    moves = []
    if move_type == MoveType.PSEUDO_LEGAL:
        moves: Iterable[Move] = board.pseudo_legal_moves(b)
    if move_type == MoveType.LEGAL:
        moves: Iterable[Move] = board.legal_moves(b)

    return moves
