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


def hash_mo(b: Board, tt: TranspositionTable) -> Iterable[SmartMove]:

    smart_moves = []
    for move in board.pseudo_legal_moves(b):
        curr_board = board.push(b, move)

        eval = 0
        if node := tt.get(board.hash(curr_board), 0):
            eval = node.value
        else:
            eval = sum(curr_board.eval, start=1)

        eval += int(move.is_capture) * (
            1000
            + PIECE_VALUE[abs(b.squares[move.end])] * 1000
            - PIECE_VALUE[abs(b.squares[move.start])]
        ) * b.turn

        smart_moves.append(SmartMove(
            move=move,
            board=curr_board,
            eval=eval,
        ))

    return sorted(
            smart_moves,
            key=lambda x: x.eval,
            reverse=b.turn == COLOR.WHITE,
        )


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
            + sum(nb.eval, start=1)
        )
    )

    return sorted(
        smart_moves,
        key=lambda x: x.eval,
        reverse=b.turn == COLOR.WHITE
    )


def simple(b: Board, tt: TranspositionTable | None = None) -> Iterable[SmartMove]:
    return sorted(
        board.smart_moves(b, lambda b, m, nb: sum(nb.eval, start=1)),
        key=lambda x: int(x.move.is_capture) * 1000 + x.eval,
        reverse=b.turn == COLOR.WHITE,
    )
