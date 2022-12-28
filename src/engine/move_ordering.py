import collections
from .constants import COLOR
from typing import Callable, Iterable, List
from .data_structures import Board, Move
from .evaluation import PIECE_VALUE
from random import shuffle

Move_ordering_fn = Callable[
    [
        Board,
        Iterable[Move],
    ],
    List[Move]
]


def fast_mvv_lva(
    b: Board,
    moves: Iterable[Move],
) -> Iterable[Move]:

    # priority collections
    mem: collections.deque[Move] = collections.deque()
    for m in moves:
        if m.is_king_capture:
            yield m
        if m.is_null:
            yield m
        if m.is_capture:
            if m.captured_piece < 2:
                mem.appendleft(m)
                continue
            yield m
        mem.append(m)
    for m in mem:
        yield m


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

    return sorted(
        moves,
        key=lambda x: eval(b, x),
        reverse=b.turn == COLOR.WHITE
    )


def no_ordering(
    b: Board,
    moves: Iterable[Move],
) -> List[Move]:
    return list(moves)


def random(
    b: Board,
    moves: Iterable[Move],
) -> List[Move]:
    moves = list(moves)
    shuffle(moves)
    return moves
