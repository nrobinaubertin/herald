#import zlib
#import time
from constants import PIECE, COLOR, CASTLE
#import hashtable
from evaluation import VALUE_MAX
from board import toUCI

def search_best_move(board, depth: int, eval_fn):

    # search_hash = board.fen()
    # start_time = time.process_time()

    best_move = None
    best_value = VALUE_MAX * -1
    for move in board.moves():
        curr_board = board.copy()
        curr_board.push(move)
        value = -alphaBeta(curr_board, VALUE_MAX * -1, VALUE_MAX, depth, eval_fn)
        # print("{}: {}\n------".format(toUCI(move), value))
        # search_hash += f",{move.uci()}:{value}"
        if value > best_value:
            best_move = move
            best_value = value

    # print(f"search time: {time.process_time() - start_time}")
    # print("hashtable size:{},req:{},hits:{}".format(len(hashtable.HASH_TABLE), hashtable.REQ, hashtable.HITS))
    # print(f"search hash: {zlib.adler32(search_hash.encode())}")
    return best_move


def alphaBeta(board, alpha: int, beta: int, depthleft: int, eval_fn) -> int:
    if not len(board.pieces[PIECE.KING * board.turn]):
        return VALUE_MAX * -1

    #if depthleft > 1:
    #    mem = hashtable.get_value(board)
    #    if mem is not None and mem.depth >= depthleft:
    #        # print("hashtable HIT, depth: {}, value: {}, hash: {}".format(mem.depth, mem.value, hashtable.hash_board(board)))
    #        return mem.value

    if depthleft == 0:
        eval = eval_fn(board)
        return eval
        # return quiescent_alphaBeta(board, VALUE_MAX * -1, VALUE_MAX, eval_fn, 0)

    value = VALUE_MAX * -1
    for move in board.moves():
        curr_board = board.copy()
        curr_board.push(move)
        value = max(value, -alphaBeta(curr_board, -beta, -alpha, depthleft - 1, eval_fn))
        alpha = max(alpha, value)
        if alpha >= beta:
            break

    #if depthleft > 1:
    #    hashtable.set_value(board, hashtable.Mem(depthleft, value))
    return value


def quiescent_alphaBeta(board, alpha: int, beta: int, eval_fn, depth: int) -> int:
    if not len(board.pieces[PIECE.KING * board.turn]):
        return VALUE_MAX * -1

    moves = list(board.moves(quiescent=True))
    if len(moves) == 0:
        return eval_fn(board)
    value = VALUE_MAX * -1
    for move in moves:
        curr_board = board.copy()
        curr_board.push(move)
        new_value = -quiescent_alphaBeta(curr_board, -beta, -alpha, eval_fn, depth + 1)
        if new_value > value:
            value = new_value
            best_move = move
        alpha = max(alpha, value)
        if alpha >= beta:
            break
    # print(board.turn, board.debug_move_stack(), best_move, value)
    return value
