import os
import datetime
import pickle
from .data_structures import Node


class TranspositionTable:
    def __init__(self, table: dict = {}):
        self.table = table
        # debug statistics
        self.hits = 0
        self.shallow_hits = 0
        self.reqs = 0
        self.nodes_added = 0
        self.better_nodes_added = 0

    def __str__(self):
        return str(self.table)

    def get(self, board_hash, depth: int = 0) -> Node:
        if __debug__:
            self.reqs += 1
        ret = self.table.get(board_hash, None)
        if __debug__:
            if ret is not None:
                self.hits += 1
                if depth != 0 and ret.depth < depth:
                    self.shallow_hits += 1
        return ret

    def add(self, board_hash, node: Node):
        if __debug__:
            self.nodes_added += 1
        if board_hash not in self.table:
            self.table[board_hash] = node
        elif self.table[board_hash].depth < node.depth:
            self.table[board_hash] = node
            if __debug__:
                self.better_nodes_added += 1

    def import_table(self, filename):
        """import a file as the table"""
        input = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "..",
            filename
        )
        with open(input, "rb") as input_pickle:
            self.table = pickle.load(input_pickle)

    def export_table(self, filename = ""):
        """export the table to a file"""
        if filename == "":
            filename = f"memory_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}",
        output = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            "..",
            filename
        )
        with open(output, "wb") as output_pickle:
            pickle.dump(self.table, output_pickle)
        return output

    def stats(self):
        return {
            "LEN": len(self.table),
            "REQ": self.reqs,
            "HITS": self.hits,
            "SHALLOW_HITS": self.shallow_hits,
            "ADD": self.nodes_added,
            "ADD_BETTER": self.better_nodes_added,
        }
