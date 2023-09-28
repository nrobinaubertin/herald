from dataclasses import dataclass

from .constants import PIECE, VALUE_MAX


@dataclass(frozen=True)
class Move:
    start: int
    end: int
    moving_piece: PIECE = PIECE.INVALID
    captured_piece: PIECE = PIECE.INVALID
    is_capture: bool = False
    is_castle: bool = False
    en_passant: int = -1
    is_king_capture: bool = False


@dataclass(frozen=True)
class Node:
    value: int
    depth: int
    pv: list[Move]
    upper: int = VALUE_MAX
    lower: int = -VALUE_MAX
    children: int = 1
