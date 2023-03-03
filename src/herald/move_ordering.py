import collections
from random import shuffle
from typing import Callable, Iterable, List

from .board import Board
from .data_structures import Move

Move_ordering_fn = Callable[
    [
        Iterable[Move],
        Board,
    ],
    List[Move],
]


def qs_ordering(
    _: Board,
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


def fast_ordering(
    _: Board,
    moves: Iterable[Move],
) -> Iterable[Move]:
    mem1: Move | None = None
    mem2: Move | None = None
    mem3: Move | None = None
    mem4: Move | None = None

    mem_list: list[Move] | None = None

    for m in moves:
        if m.is_king_capture or m.is_castle:
            yield m
        # if board.will_check_the_king(b, m):
        #     yield m
        if m.is_capture:
            # if m.captured_piece < 2:
            #     mem.appendleft(m)
            #     continue
            if m.captured_piece > 4:
                yield m
                continue
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
            continue
        if mem_list is None:
            mem_list = []
        mem_list.append(m)
    if mem4:
        yield mem4
    if mem3:
        yield mem3
    if mem2:
        yield mem2
    if mem1:
        yield mem1
    if mem_list is not None:
        for m in mem_list:
            yield m


def fast_mvv_lva(
    _: Board,
    moves: Iterable[Move],
) -> Iterable[Move]:
    # priority collections
    mem: collections.deque[Move] = collections.deque()
    for m in moves:
        if m.is_king_capture or m.is_castle:
            yield m
        # if board.will_check_the_king(b, m):
        #     yield m
        if m.is_capture:
            if m.captured_piece < 2:
                mem.appendleft(m)
                continue
            yield m
        mem.append(m)
    for m in mem:
        yield m


def no_ordering(
    _: Board,
    moves: Iterable[Move],
) -> List[Move]:
    return list(moves)


def random(
    _: Board,
    moves: Iterable[Move],
) -> List[Move]:
    moves = list(moves)
    shuffle(moves)
    return moves
