import collections
from random import shuffle
from typing import Callable, Iterable, List

from . import board
from .constants import COLOR
from .data_structures import Board, Move
from .evaluation import PIECE_VALUE

Move_ordering_fn = Callable[
    [
        Board,
        Iterable[Move],
    ],
    List[Move],
]


def qs_ordering(
    b: Board,
    moves: Iterable[Move],
) -> Iterable[Move]:

    mem1: Move | None = None
    mem2: Move | None = None
    mem3: Move | None = None
    mem4: Move | None = None

    for m in moves:
        if m.is_king_capture:
            yield m
        if m.captured_piece > 3:
            yield m
        if mem1 is None:
            mem1 = m
            continue
        if mem2 is None:
            mem2 = m
            continue
        if mem3 is None:
            mem3 = m
            continue
        if mem4 is None:
            mem4 = m
            continue
        if m.captured_piece < mem1.captured_piece:
            m, mem1 = mem1, m
        if m.captured_piece < mem2.captured_piece:
            m, mem2 = mem2, m
        if m.captured_piece < mem3.captured_piece:
            m, mem3 = mem3, m
        if m.captured_piece < mem4.captured_piece:
            m, mem4 = mem4, m
        yield m
    if mem4:
        yield mem4
    if mem3:
        yield mem3
    if mem2:
        yield mem2
    if mem1:
        yield mem1


def fast_mvv_lva(
    b: Board,
    moves: Iterable[Move],
) -> Iterable[Move]:

    # priority collections
    mem: collections.deque[Move] = collections.deque()
    for m in moves:
        if m.is_king_capture or m.is_castle:
            yield m
        b2 = board.push(b, m)
        if board.is_square_attacked(b2, board.king_square(b2, b2.turn), b.turn):
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
        b2 = board.push(b, m)
        if board.is_square_attacked(b2, board.king_square(b2, b2.turn), b.turn):
            return 100000
        if m.is_castle:
            return 99999
        return (
            int(m.is_capture)
            * (
                100
                + PIECE_VALUE[abs(b.squares[m.end])] * 100
                - PIECE_VALUE[abs(b.squares[m.start])]
            )
            * b.turn
        )

    return sorted(moves, key=lambda x: eval(b, x), reverse=b.turn == COLOR.WHITE)


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
