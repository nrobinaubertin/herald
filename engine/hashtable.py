import collections
import enum
import board

HASH_TABLE = {}
REQ = 0
HITS = 0

class NODE_TYPE(enum.IntEnum):
    PV = 0,
    ALL = 1,
    CUT = -1,

Node = collections.namedtuple('Node', ['board', 'depth', 'value', 'type', 'upper', 'lower'])

def get_stats():
    global HASH_TABLE
    global HITS
    global REQ
    return [len(HASH_TABLE), REQ, HITS]

def get_value(board) -> Node:
    global HASH_TABLE
    global HITS
    global REQ
    ret = HASH_TABLE.get(board.hash(), None)
    if ret is not None:
        HITS += 1
    REQ += 1
    return ret

def set_value(node: Node):
    global HASH_TABLE
    hash = node.board.hash()
    if hash not in HASH_TABLE:
        HASH_TABLE[hash] = node
    elif HASH_TABLE[hash].depth < node.depth:
        HASH_TABLE[hash] = node
