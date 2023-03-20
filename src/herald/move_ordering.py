from random import shuffle
from typing import Callable, Iterable, List

from . import pruning
from .board import Board
from .constants import PIECE
from .data_structures import Move

Move_ordering_fn = Callable[
    [
        Iterable[Move],
        Board,
    ],
    List[Move],
]


def capture_ordering(
    _: Board,
    moves: Iterable[Move],
) -> Iterable[Move]:
    mem1: Move | None = None
    mem2: Move | None = None
    mem3: Move | None = None
    mem4: Move | None = None

    for m in moves:
        # promotions are highly valued
        if m.moving_piece == PIECE.PAWN and (m.end < 30 or m.end > 90):
            yield m
        if not m.is_capture:
            continue
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
    b: Board,
    moves: Iterable[Move],
) -> Iterable[Move]:
    captures: list[Move] = []
    usuals: list[Move] = []
    bad_captures: list[Move] = []

    for m in moves:
        # promotions are highly valued
        if m.moving_piece == PIECE.PAWN and (m.end < 30 or m.end > 90):
            yield m
        if m.is_king_capture:
            yield m
        if m.is_capture:
            if pruning.is_bad_capture(b, m):
                bad_captures.append(m)
                continue
            if m.captured_piece > 3:
                yield m
                continue
            captures.append(m)
        usuals.append(m)
    yield from captures
    yield from usuals
    yield from bad_captures


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
