from dataclasses import dataclass, field

from .board import Board
from .data_structures import Move, Node


@dataclass
class Config:
    version: str = "0.21"
    name: str = "Herald"
    author: str = "Niels Robin-Aubertin"
    transposition_table: dict[
        Board,
        Node,
    ] = field(default_factory=dict)
    hash_move_tt: dict[
        Board,
        Move,
    ] = field(default_factory=dict)
    opening_book: dict[
        str,
        str,
    ] = field(default_factory=dict)
    use_transposition_table: bool = False
    use_hash_move: bool = False
    use_killer_moves: bool = False
    use_saved_search: bool = False
    quiescence_search: bool = False
    quiescence_depth: int = 0
