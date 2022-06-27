import collections
import enum
import board

HASH_TABLE = {}
if __debug__:
    REQ = 0
    HITS = 0
    ADD = 0
    ADD_BETTER = 0
    SHALLOW_HITS = 0

if __debug__:
    def stats():
        global HASH_TABLE
        global HITS
        global REQ
        global ADD
        global ADD_BETTER
        return {
            "LEN": len(HASH_TABLE),
            "REQ": REQ,
            "HITS": HITS,
            "ADD": ADD,
            "ADD_BETTER": ADD_BETTER,
            "SHALLOW_HITS": SHALLOW_HITS,
        }

def get(hash, depth):
    if __debug__:
        global HASH_TABLE
        global REQ
        REQ += 1
    ret = HASH_TABLE.get(hash, None)
    if __debug__:
        if ret is not None:
            global HITS
            HITS += 1
            if ret.depth < depth:
                global SHALLOW_HITS
                SHALLOW_HITS += 1
    return ret

def add(hash, node):
    global HASH_TABLE
    global ADD
    global ADD_BETTER
    ADD += 1
    if hash not in HASH_TABLE:
        HASH_TABLE[hash] = node
    elif HASH_TABLE[hash].depth < node.depth:
        ADD_BETTER += 1
        HASH_TABLE[hash] = node
