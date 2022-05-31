import collections
import board

HASH_TABLE = {}
REQ = 0
HITS = 0

Mem = collections.namedtuple('Mem', ['depth', 'value'])

def get_value(board) -> Mem:
    global HASH_TABLE
    global HITS
    global REQ
    ret = HASH_TABLE.get(board.hash(), None)
    if ret is not None:
        HITS += 1
    REQ += 1
    return ret

def set_value(board, mem: Mem):
    global HASH_TABLE
    HASH_TABLE[board.hash()] = mem
