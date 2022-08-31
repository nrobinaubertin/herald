import os
import datetime
import pickle
from array import array
import hashlib
import multiprocessing
import multiprocessing.managers
from typing import Hashable
from .data_structures import Node, Board



def hash(b: Board) -> Hashable:
    data = array("b")
    data.extend(b.squares)
    data.append(b.turn)
    data.extend(b.castling_rights)
    data.append(b.en_passant)
    data.append(b.king_en_passant)
    return data.tobytes()
    # return hashlib.sha256(data).hexdigest()


class TranspositionTable:
    # def __init__(self, table: dict[Hashable, Node] | multiprocessing.managers.DictProxy[Hashable, Node] = {}) -> None:
    def __init__(self, table={}) -> None:
        self.table = table
        # debug statistics
        self.hits = 0
        self.shallow_hits = 0
        self.old_hits = 0
        self.reqs = 0
        self.nodes_added = 0
        self.better_nodes_added = 0

    def __str__(self) -> str:
        return str(self.table)

    def get(self, b: Board, depth: int = 0) -> Node | None:
        try:
            board_hash = hash(b)
            if __debug__:
                self.reqs += 1
            ret = self.table.get(board_hash, None)
            if ret is not None:
                if __debug__:
                    self.hits += 1
                if b.full_move < ret.full_move + ret.depth - 2:
                    if __debug__:
                        self.old_hits += 1
                    del self.table[board_hash]
                    return None
                if depth != 0 and ret.depth < depth:
                    if __debug__:
                        self.shallow_hits += 1
                    return None
            return ret
        except:
            return None

    def add(self, b: Board, node: Node) -> None:
        board_hash = hash(b)
        if __debug__:
            self.nodes_added += 1
        if board_hash not in self.table:
            self.table[board_hash] = node
        elif self.table[board_hash].depth < node.depth:
            self.table[board_hash] = node
            if __debug__:
                self.better_nodes_added += 1

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
            "LEN": len(self.table),
            "REQ": self.reqs,
            "HITS": self.hits,
            "SHALLOW_HITS": self.shallow_hits,
            "OLD_HITS": self.old_hits,
            "ADD": self.nodes_added,
            "ADD_BETTER": self.better_nodes_added,
        }
