import collections
import time
from constants import PIECE, COLOR, CASTLE
import hashtable
from evaluation import VALUE_MAX, PIECE_VALUE

QUIESCENT_NODES = 0
ALPHA_NODES = 0
LEAF_NODES = 0

Search = collections.namedtuple("Search", ["move", "depth", "score", "nodes", "time"])


def search(board, depth: int):

    start_time = time.process_time_ns()

    global QUIESCENT_NODES
    global ALPHA_NODES
    global LEAF_NODES

    QUIESCENT_NODES = 0
    ALPHA_NODES = 0
    LEAF_NODES = 0
    best_move = None
    best_value = (VALUE_MAX * -1) - 1
    for move in board.moves():
        curr_board = board.copy()
        curr_board.push(move)
        value = aspirationWindow(curr_board, board.eval, depth)
        if value > best_value:
            best_move = move
            best_value = value

    return Search(
        move=best_move,
        depth=depth,
        nodes=LEAF_NODES,
        score=best_value,
        time=(time.process_time_ns() - start_time),
    )


def aspirationWindow(board, guess: int, depth: int) -> int:
    lower = guess - 50
    upper = guess + 50
    iteration = 0
    while True:
        iteration += 1
        score = negaC(board, lower, upper, depth)
        if score > upper:
            upper += 100 * (iteration**2)
            continue
        if score < lower:
            lower -= 100 * (iteration**2)
            continue
        break
    return score


def negaC(board, min: int, max: int, depth: int) -> int:
    score = min
    while min < max:
        alpha = (min + max + 1) // 2
        score = alphaBetaFailSoft(board, alpha, alpha + 100, depth)
        if score > alpha:
            min = score
        else:
            max = score
    return score


def alphaBetaFailSoft(board, alpha: int, beta: int, depth: int) -> int:
    if not len(board.pieces[PIECE.KING * board.turn]):
        return VALUE_MAX * -1

    if depth > 0:
        mem = hashtable.get_value(board)
        if mem is not None and mem.depth >= depth:
            return mem.value

    if depth == 0:
        global LEAF_NODES
        LEAF_NODES += 1
        return board.eval * abs(board.turn) // board.turn

    global ALPHA_NODES
    ALPHA_NODES += 1

    best_score = (VALUE_MAX * -1) - 1
    for move in board.pseudo_legal_moves():
        curr_board = board.copy()
        curr_board.push(move)
        score = -alphaBetaFailSoft(curr_board, -beta, -alpha, depth - 1)
        if score >= beta:
            return score
        if score > best_score:
            best_score = score
            if score > alpha:
                alpha = score

    if depth > 0:
        hashtable.set_value(board, hashtable.Mem(depth, best_score))
    return best_score


#def quiescent_alphaBeta(board, alpha: int, beta: int, depth: int) -> int:
#    if not len(board.pieces[PIECE.KING * board.turn]):
#        return VALUE_MAX * -1
#
#    mem = hashtable.get_value(board)
#    if mem is not None:
#        return mem.value
#
#    global QUIESCENT_NODES
#    QUIESCENT_NODES += 1
#
#    # moves = [x for x in board.pseudo_legal_moves(quiescent=True) if PIECE_VALUE[abs(board.squares[x.end])] >= PIECE_VALUE[abs(board.squares[x.start])]]
#    # moves = [x for x in board.pseudo_legal_moves(quiescent=True)]# if PIECE_VALUE[abs(board.squares[x.end])] >= PIECE_VALUE[abs(board.squares[x.start])]]
#
#    # if len(moves) == 0:
#    #    return eval_fn(board)
#
#    value = (VALUE_MAX * -1) - 1
#
#    if depth < 10:
#        for move in board.pseudo_legal_moves(quiescent=True):
#            # No time to implement SEE (https://www.chessprogramming.org/Static_Exchange_Evaluation)
#            # This should avoid glaring mistakes
#            if (
#                PIECE_VALUE[abs(board.squares[move.end])]
#                < PIECE_VALUE[abs(board.squares[move.start])]
#            ):
#                continue
#            # if depth > 50:
#            #    QUIESCENT_NODES += 1
#            #    print(board)
#            #    print(move, board.squares[move.start], board.squares[move.end])
#            #    sys.exit()
#            curr_board = board.copy()
#            curr_board.push(move)
#            value = max(
#                value,
#                -quiescent_alphaBeta(curr_board, -beta, -alpha, depth + 1),
#            )
#            alpha = max(alpha, value)
#            if alpha >= beta:
#                break
#    # print(board.turn, board.debug_move_stack(), best_move, value)
#
#    if value == (VALUE_MAX * -1) - 1:
#        return eval_fn(board)
#
#    return value
