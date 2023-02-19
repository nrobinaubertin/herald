"""Storage class for usual transposition table."""

# The table size is the maximum number of elements in the transposition table.
TABLE_SIZE = 1_000_000


class TranspositionTable:
    def __init__(self, table=None) -> None:
        self.table = table or {}
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
            if __debug__:
                self.table["reqs"] += 1
            ret = self.table.get(board, None)
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
        if __debug__:
            self.table["nodes_added"] += 1
        if board not in self.table:
            self.table[board] = node
        elif self.table[board].depth < node.depth:
            self.table[board] = node
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
