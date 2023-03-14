from random import shuffle
from typing import Callable, Iterable, List

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
    _: Board,
    moves: Iterable[Move],
) -> Iterable[Move]:
    captures: list[Move] = []
    usuals: list[Move] = []

    for m in moves:
        # promotions are highly valued
        if m.moving_piece == PIECE.PAWN and (m.end < 30 or m.end > 90):
            yield m
        if m.is_king_capture:
            yield m
        if m.is_capture:
            if m.captured_piece > 3:
                yield m
                continue
            if captures is None:
                captures = []
            captures.append(m)
        usuals.append(m)
    yield from captures
    yield from usuals


def no_ordering(
    _: Board,
    moves: Iterable[Move],
) -> List[Move]:
    return list(moves)


def tactical_ordering(
    moves: Iterable[Move],
):
    def eval_move(m: Move) -> int:
        if m.is_king_capture:
            return 9999
        if m.moving_piece == PIECE.PAWN and (m.end < 30 or m.end > 90):
            return 600
        if m.is_capture:
            if m.captured_piece == PIECE.QUEEN:
                return 500
            if m.captured_piece == PIECE.ROOK:
                return 400
            if m.captured_piece == PIECE.BISHOP:
                return 300
            if m.captured_piece == PIECE.KNIGHT:
                return 200
            if m.captured_piece == PIECE.PAWN:
                return 100
            return 100
        if m.is_castle:
            return 1
        return 0

    return sorted(moves, key=eval_move)
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


def random(
    _: Board,
    moves: Iterable[Move],
) -> List[Move]:
    moves = list(moves)
    shuffle(moves)
    return moves
