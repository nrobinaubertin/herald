from typing import Iterable

from . import pruning
from .board import Board
from .constants import PIECE
from .data_structures import Move


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
