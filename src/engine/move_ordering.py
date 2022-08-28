from .constants import COLOR
from . import board
from .data_structures import SmartMove, Board
from .evaluation import PIECE_VALUE


def mvv_lva(b: Board) -> list[SmartMove]:
    smart_moves: list[SmartMove] = [x for x in board.smart_moves(
        b,
        lambda b, m, nb: (
            int(m.is_capture)
            * (
                1000
                + PIECE_VALUE[abs(b.squares[m.end])] * 100
                - PIECE_VALUE[abs(b.squares[m.start])]
            ) * b.turn
            + sum(nb.eval, start=1)
        )
    )]

    return sorted(
        smart_moves,
        key=lambda x: x.eval,
        reverse=b.turn == COLOR.WHITE
    )


def simple(b: Board) -> list[SmartMove]:
    smart_moves: list[SmartMove] = [x for x in board.smart_moves(
        b,
        lambda b, m, nb: sum(nb.eval, start=1)
    )]

    ordered_smart_captures = sorted(
        filter(lambda x: x.move.is_capture, smart_moves),
        key=lambda x: x.eval,
        reverse=b.turn == COLOR.WHITE,
    )

    ordered_smart_normal = sorted(
        filter(lambda x: not x.move.is_capture, smart_moves),
        key=lambda x: x.eval,
        reverse=b.turn == COLOR.WHITE,
    )

    return ordered_smart_captures + ordered_smart_normal
