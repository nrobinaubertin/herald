"""Storage class for usual transposition table."""

from array import array
from typing import Hashable

# The table size is the maximum number of elements in the transposition table.
TABLE_SIZE = 1_000_000


def hash(board) -> Hashable:
    data = array("b")
    data.extend(board.squares)
    data.append(board.turn)
    data.extend(board.castling_rights)
    data.append(board.en_passant)
    data.append(board.king_en_passant)
    return data.tobytes()


class TranspositionTable:
    def __init__(self, table={}) -> None:
        self.table = table
        # debug statistics
        self.table["hits"] = 0
        self.table["shallow_hits"] = 0
        self.table["old_hits"] = 0
        self.table["reqs"] = 0
        self.table["nodes_added"] = 0
        self.table["better_nodes_added"] = 0
        self.table["worse_nodes_added"] = 0

    def __str__(self) -> str:
        return str(self.table)

    def clear(self):
        self.table.clear()
        self.table["hits"] = 0
        self.table["shallow_hits"] = 0
        self.table["old_hits"] = 0
        self.table["reqs"] = 0
        self.table["nodes_added"] = 0
        self.table["better_nodes_added"] = 0
        self.table["worse_nodes_added"] = 0

    def get(self, board, depth: int = 0):
        try:
            board_hash = hash(board)
            if __debug__:
                self.table["reqs"] += 1
            ret = self.table.get(board_hash, None)
            if ret is not None:
                if __debug__:
                    self.table["hits"] += 1
                if __debug__ and ret.depth < depth:
                    self.table["shallow_hits"] += 1
            return ret
        except:
            return None

    def add(self, board, node) -> None:
        if len(self.table) > TABLE_SIZE:
            self.table.clear()
        board_hash = hash(board)
        if __debug__:
            self.table["nodes_added"] += 1
        if board_hash not in self.table:
            self.table[board_hash] = node
        elif self.table[board_hash].depth < node.depth:
            self.table[board_hash] = node
            if __debug__:
                self.table["better_nodes_added"] += 1
        elif __debug__:
            self.table["worse_nodes_added"] += 1

    def stats(self) -> dict[str, int]:
        return {
            "LEN": len(self.table) - 6,
            "REQ": self.table["reqs"],
            "HITS": self.table["hits"],
            "SHALLOW_HITS": self.table["shallow_hits"],
            "OLD_HITS": self.table["old_hits"],
            "ADD": self.table["nodes_added"],
            "ADD_BETTER": self.table["better_nodes_added"],
            "ADD_WORSE": self.table["worse_nodes_added"],
        }
