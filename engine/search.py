import collections
import time
from constants import PIECE, COLOR, CASTLE
import hashtable
from evaluation import VALUE_MAX, PIECE_VALUE, eval
from board import toUCI

QUIESCENT_NODES = 0
LEAF_NODES = 0
ENABLE_HASHTABLE = False

Search = collections.namedtuple("Search", ["move", "depth", "score", "nodes", "time", "best_node"])


def search(board, depth: int, debug: bool = False, scan_move: str = ""):

    start_time = time.process_time_ns()

    global QUIESCENT_NODES
    global LEAF_NODES

    QUIESCENT_NODES = 0
    LEAF_NODES = 0
    best_node = hashtable.Node(
        board=board,
        depth=depth,
        value=(VALUE_MAX if board.turn == COLOR.BLACK else -VALUE_MAX),
        type=hashtable.NODE_TYPE.PV,
        lower=-VALUE_MAX,
        upper=VALUE_MAX,
    )
    best_move = None
    for move in board.moves():
        curr_board = board.copy()
        curr_board.moves_history = collections.deque() # erase history to cleanly display pv
        curr_board.push(move)
        #node = aspirationWindow(curr_board, board.eval, depth, debug, scan_move)
        #node = negaC(curr_board, -VALUE_MAX, VALUE_MAX, depth)
        node = alphaBeta(curr_board, -VALUE_MAX, VALUE_MAX, depth, debug, scan_move)
        #print(
        #    ""
        #    + f"info "
        #    + f"score cp {node.value} "
        #    + f"pv {' '.join([toUCI(x) for x in node.board.moves_history])}"
        #)
        if board.turn == COLOR.WHITE:
            if node.value > best_node.value:
                best_node = hashtable.Node(
                    board=node.board,
                    depth=depth,
                    value=node.value,
                    type=node.type,
                    lower=-VALUE_MAX,
                    upper=VALUE_MAX,
                )
                best_move = move
        else:
            if node.value < best_node.value:
                best_node = hashtable.Node(
                    board=node.board,
                    depth=depth,
                    value=node.value,
                    type=node.type,
                    lower=-VALUE_MAX,
                    upper=VALUE_MAX,
                )
                best_move = move

    return Search(
        move=best_move,
        depth=depth,
        nodes=LEAF_NODES,
        score=best_node.value,
        time=(time.process_time_ns() - start_time),
        best_node=best_node
    )


def aspirationWindow(board, guess: int, depth: int, debug: bool = False, scan_move: str = "") -> hashtable.Node:
    lower = guess - 50
    upper = guess + 50
    iteration = 0
    while True:
        iteration += 1
        #node = negaC(board, lower, upper, depth)
        node = alphaBeta(board, lower, upper, depth, debug, scan_move)
        if node.value > upper:
            upper += 100 * (iteration**2)
            continue
        if node.value < lower:
            lower -= 100 * (iteration**2)
            continue
        break
    return node


# In my tests, negaC was slower than just using an aspiration window
#def negaC(board, min: int, max: int, depth: int) -> hashtable.Node:
#    while min < max - 1:
#        alpha = (min + max + 1) // 2
#        node = alphaBeta(board, alpha, alpha + 100, depth)
#        if node.value > alpha:
#            min = node.value
#        else:
#            max = node.value
#    return node


def alphaBeta(board, alpha: int, beta: int, depth: int, debug: bool = False, scan_move: str = "") -> hashtable.Node:
    global ENABLE_HASHTABLE
    global LEAF_NODES

    # TERMINAL nodes (aka LEAF nodes)
    if not len(board.pieces[PIECE.KING * board.turn]):
        LEAF_NODES += 1
        return hashtable.Node(
            value=-VALUE_MAX,
            board=board,
            depth=depth,
            type=hashtable.NODE_TYPE.PV,
            lower=alpha,
            upper=beta,
        )
    if depth == 0:
        LEAF_NODES += 1
        return hashtable.Node(
            value=board.eval, #eval(board),
            board=board,
            depth=depth,
            type=hashtable.NODE_TYPE.PV,
            lower=alpha,
            upper=beta,
        )

    # Check for transposition node
    if depth > 0 and ENABLE_HASHTABLE:
        node = hashtable.get_value(board)
        if node is not None and node.depth >= depth:
            #if depth >= 3:
            #    print(
            #        f"info depth {depth} score cp {node.value} alpha {alpha} beta {beta} "
            #        + f"pv {' '.join([toUCI(x) for x in node.board.moves_history])}"
            #    )
            #if alpha <= node.value <= beta:
                #print(f"TP, [{alpha}, {node.value}, {beta}]")
            return node

    # Explicit minimax with soft alpha-beta pruning
    if board.turn == COLOR.WHITE:
        node = hashtable.Node(
            board=board,
            depth=depth,
            value=-VALUE_MAX,
            type=hashtable.NODE_TYPE.PV,
            lower=-VALUE_MAX,
            upper=VALUE_MAX,
        )
        for move in board.pseudo_legal_moves():
            curr_board = board.copy()
            curr_board.push(move)
            nn = alphaBeta(curr_board, alpha, beta, depth - 1, debug, scan_move)
            if debug and scan_move in [toUCI(x) for x in nn.board.moves_history] and depth > 2:
                print(
                    f"info depth {depth} score cp {nn.value} alpha {alpha} beta {beta} "
                    + f"pv {' '.join([toUCI(x) for x in nn.board.moves_history])}"
                )
            if nn.value > node.value:
                node = hashtable.Node(
                    value=nn.value,
                    board=nn.board,
                    depth=depth,
                    type=nn.type,
                    lower=alpha,
                    upper=beta,
                )
            alpha = max(alpha, nn.value)
            if nn.value >= beta:
                # Save the resulting node in the transposition table
                if depth > 0 and ENABLE_HASHTABLE:
                    hashtable.set_value(node)
                return hashtable.Node(
                    value=nn.value,
                    board=nn.board,
                    depth=depth,
                    type=hashtable.NODE_TYPE.CUT,
                    lower=alpha,
                    upper=beta,
                )
    else:
        node = hashtable.Node(
            board=board,
            depth=depth,
            value=VALUE_MAX,
            type=hashtable.NODE_TYPE.PV,
            lower=-VALUE_MAX,
            upper=VALUE_MAX,
        )
        for move in board.pseudo_legal_moves():
            curr_board = board.copy()
            curr_board.push(move)
            nn = alphaBeta(curr_board, alpha, beta, depth - 1, debug, scan_move)
            if nn.value < node.value:
                node = hashtable.Node(
                    value=nn.value,
                    board=nn.board,
                    depth=depth,
                    type=nn.type,
                    lower=alpha,
                    upper=beta,
                )
                if debug and scan_move in [toUCI(x) for x in nn.board.moves_history] and depth > 2:
                    print(
                        f"info depth {depth} score cp {nn.value} alpha {alpha} beta {beta} "
                        + f"pv {' '.join([toUCI(x) for x in nn.board.moves_history])}"
                    )
            beta = min(beta, nn.value)
            if nn.value <= alpha:
                # Save the resulting node in the transposition table
                if depth > 0 and ENABLE_HASHTABLE:
                    hashtable.set_value(node)
                return hashtable.Node(
                    value=nn.value,
                    board=nn.board,
                    depth=depth,
                    type=hashtable.NODE_TYPE.CUT,
                    lower=alpha,
                    upper=beta,
                )

    # Save the resulting node in the transposition table
    if depth > 0 and ENABLE_HASHTABLE:
        hashtable.set_value(node)

    return node


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
