import os
import datetime
import pickle
from array import array
from typing import Hashable
from .data_structures import Node, Board

# The table size is the maximum number of elements in the transposition table.
TABLE_SIZE = 1_000_000


def hash(b: Board) -> Hashable:
    data = array("b")
    data.extend(b.squares)
    data.append(b.turn)
    data.extend(b.castling_rights)
    data.append(b.en_passant)
    data.append(b.king_en_passant)
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

    def get(self, b: Board, depth: int = 0) -> Node | None:
        try:
            board_hash = hash(b)
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

    def add(self, b: Board, node: Node) -> None:
        if len(self.table) > TABLE_SIZE:
            self.table.clear()
        board_hash = hash(b)
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

    def import_table(self, filename: str) -> None:
        """import a file as the table"""
        input = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "..",
            filename,
        )
        with open(input, "rb") as input_pickle:
            self.table = pickle.load(input_pickle)

    def export_table(self, filename: str = "") -> str:
        """export the table to a file"""
        if filename == "":
            filename = (
                f"memory_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
            )
        output = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "..",
            filename,
        )
        with open(output, "wb") as output_pickle:
            pickle.dump(self.table, output_pickle)
        return output

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
