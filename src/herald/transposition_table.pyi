from typing import Hashable, Union

from _typeshed import Incomplete

from herald.data_structures import Board as Board
from herald.data_structures import Node as Node

TABLE_SIZE: int

def hash(b: Board) -> Hashable: ...

class TranspositionTable:
    table: Incomplete
    def __init__(self, table=...) -> None: ...
    def clear(self) -> None: ...
    def get(self, board: Board, depth: int = ...) -> Union[Node, None]: ...
    def add(self, board: Board, node: Node) -> None: ...
    def import_table(self, filename: str) -> None: ...
    def export_table(self, filename: str = ...) -> str: ...
    def stats(self) -> dict[str, int]: ...
