import zlib
import time
from constants import PIECE, COLOR, CASTLE
import hashtable
from evaluation import VALUE_MAX, PIECE_VALUE
from board import toUCI

QUIESCENT_NODES = 0
ALPHA_NODES = 0

def search_best_move(board, depth: int, eval_fn):

    #search_hash = ""
    #start_time = time.process_time()

    global QUIESCENT_NODES
    global ALPHA_NODES
    best_move = None
    best_value = (VALUE_MAX * -1) - 1
    QUIESCENT_NODES = 0
    ALPHA_NODES = 0
    for move in board.moves():
        curr_board = board.copy()
        curr_board.push(move)
        value = -alphaBeta(curr_board, VALUE_MAX * -1, VALUE_MAX, depth, eval_fn)
        #print("SEARCH {}: {}\n------".format(toUCI(move), value))
        #search_hash += f",{toUCI(move)}:{value}"
        if value > best_value:
            best_move = move
            best_value = value

    #print(f"Alpha nodes: {ALPHA_NODES}")
    #print(f"Qiescent nodes: {QUIESCENT_NODES}")
    #print(f"search time: {time.process_time() - start_time}")
    #print("hashtable size:{},req:{},hits:{}".format(len(hashtable.HASH_TABLE), hashtable.REQ, hashtable.HITS))
    #print(f"search hash: {zlib.adler32(search_hash.encode())}")
    return best_move


def alphaBeta(board, alpha: int, beta: int, depthleft: int, eval_fn) -> int:
    if not len(board.pieces[PIECE.KING * board.turn]):
        return VALUE_MAX * -1

    if depthleft > 0:
        mem = hashtable.get_value(board)
        if mem is not None and mem.depth >= depthleft:
            # print("hashtable HIT, depth: {}, value: {}, hash: {}".format(mem.depth, mem.value, hashtable.hash_board(board)))
            return mem.value

    if depthleft == 0:
        eval1 = eval_fn(board)
        #eval2 = quiescent_alphaBeta(board, VALUE_MAX * -1, VALUE_MAX, eval_fn, 0)
        return eval1
        #return (eval1 + eval2) // 2

    global ALPHA_NODES
    ALPHA_NODES += 1

    value = (VALUE_MAX * -1) - 1
    for move in board.pseudo_legal_moves():
        curr_board = board.copy()
        curr_board.push(move)
        value = max(value, -alphaBeta(curr_board, -beta, -alpha, depthleft - 1, eval_fn))
        alpha = max(alpha, value)
        #print("ALPHA {}: {}\n".format(toUCI(move), value))
        if alpha >= beta:
            break

    if depthleft > 0:
        hashtable.set_value(board, hashtable.Mem(depthleft, value))
    return value


def quiescent_alphaBeta(board, alpha: int, beta: int, eval_fn, depth: int) -> int:
    if not len(board.pieces[PIECE.KING * board.turn]):
        return VALUE_MAX * -1

    mem = hashtable.get_value(board)
    if mem is not None:
        return mem.value

    global QUIESCENT_NODES
    QUIESCENT_NODES += 1

    #moves = [x for x in board.pseudo_legal_moves(quiescent=True) if PIECE_VALUE[abs(board.squares[x.end])] >= PIECE_VALUE[abs(board.squares[x.start])]]
    #moves = [x for x in board.pseudo_legal_moves(quiescent=True)]# if PIECE_VALUE[abs(board.squares[x.end])] >= PIECE_VALUE[abs(board.squares[x.start])]]

    #if len(moves) == 0:
    #    return eval_fn(board)

    value = (VALUE_MAX * -1) - 1

    if depth < 10:
        for move in board.pseudo_legal_moves(quiescent=True):
            # No time to implement SEE (https://www.chessprogramming.org/Static_Exchange_Evaluation)
            # This should avoid glaring mistakes
            if PIECE_VALUE[abs(board.squares[move.end])] < PIECE_VALUE[abs(board.squares[move.start])]:
                continue
            #if depth > 50:
            #    QUIESCENT_NODES += 1
            #    print(board)
            #    print(move, board.squares[move.start], board.squares[move.end])
            #    sys.exit()
            curr_board = board.copy()
            curr_board.push(move)
            value = max(value, -quiescent_alphaBeta(curr_board, -beta, -alpha, eval_fn, depth + 1))
            #print("QUIET {}: {}\n".format(toUCI(move), value))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
    # print(board.turn, board.debug_move_stack(), best_move, value)

    if value == (VALUE_MAX * -1) - 1:
        return eval_fn(board)

    return value
