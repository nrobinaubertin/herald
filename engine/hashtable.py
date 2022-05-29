import collections
import board_simple

HASH_TABLE = {}
REQ = 0
HITS = 0

Mem = collections.namedtuple('Mem', ['depth', 'value'])

def hash_board(board) -> str:
    return ",".join(board.fen().split()[:2])

def get_value(board) -> Mem:
    global HASH_TABLE
    global HITS
    global REQ
    ret = HASH_TABLE.get(hash_board(board), None)
    if ret is not None:
        HITS += 1
    REQ += 1
    return ret

def set_value(board, mem: Mem):
    global HASH_TABLE
    HASH_TABLE[hash_board(board)] = mem
