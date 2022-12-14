from .constants import COLOR, PIECE
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
    tt: TranspositionTable | None = None,
    move_type: MoveType = MoveType.PSEUDO_LEGAL,
) -> Iterable[Move]:

    moves: Iterable[Move] = []
    if move_type == MoveType.QUIESCENT:
        moves = [
            x for x in board.pseudo_legal_moves(b, quiescent=True)
            if not is_bad_capture(b, x)
        ]
    if move_type == MoveType.PSEUDO_LEGAL:
        moves = board.pseudo_legal_moves(b)
    if move_type == MoveType.LEGAL:
        moves = board.legal_moves(b)

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

    moves: Iterable[Move] = []
    if move_type == MoveType.QUIESCENT:
        moves = [
            x for x in board.pseudo_legal_moves(b, quiescent=True)
            if not is_bad_capture(b, x)
        ]
    if move_type == MoveType.PSEUDO_LEGAL:
        moves = board.pseudo_legal_moves(b)
    if move_type == MoveType.LEGAL:
        moves = board.legal_moves(b)

    return moves
