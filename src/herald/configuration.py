from dataclasses import dataclass, field
from typing import Any

from .board import Board
from .data_structures import Move, Node


@dataclass
class Config:
    quiescence_fn: Any
    move_ordering_fn: Any
    alg_fn: Any
    version: str = "0.20.8"
    name: str = "Herald"
    author: str = "nrobinaubertin"
    transposition_table: dict[Board, Node] = field(default_factory=dict)
    hash_move_tt: dict[Board, Move] = field(default_factory=dict)
    opening_book: dict[str, str] = field(default_factory=dict)
    use_transposition_table: bool = False
    use_hash_move: bool = False
    use_killer_moves: bool = False
    quiescence_search: bool = False
    quiescence_depth: int = 0
