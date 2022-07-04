"""
Search alogrithms
A "validated" algorithm is one that does give the same result as minimax (with full pv equality)
_tt algorithms can be validated by only taking tt_nodes with the same depth as the current pass
"""

from collections import deque, namedtuple
from engine.constants import PIECE, COLOR
import engine.hashtable
from engine.evaluation import VALUE_MAX, eval_board, move_eval
from engine.board import toUCI, Board

Node = namedtuple(
    "Node",
    ["value", "depth", "pv", "type", "upper", "lower", "squares", "children"],
    defaults=[deque(), None, -VALUE_MAX, VALUE_MAX, None, 0],
)
SmartMove = namedtuple("SmartMove", ["move", "board", "eval"])

if __debug__:
    COLLISIONS = 0
    NODE_DEPTH = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# alphabeta pruning (fail-soft) with move ordering and tt
# not validated
def alphabeta_tt_mo(board: Board, alpha: int, beta: int, depth: int, pv: deque) -> Node:

    if __debug__:
        global NODE_DEPTH
        NODE_DEPTH[depth] += 1

    # we check if there's no king of our color
    # in that case we can stop there
    if len(board.pieces[PIECE.KING * board.turn]) == 0:
        return Node(
            value=-VALUE_MAX * board.turn,
            depth=depth,
            pv=pv,
        )

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return Node(
            value=eval_board(board),
            depth=0,
            pv=pv,
        )

    # check if we find a hit in the transposition table
    node = engine.hashtable.get(board.hash(), depth)
    if node is not None:
        if node.depth >= depth:
            return Node(
                value=node.value,
                pv=pv,
                depth=node.depth,
            )

    # placeholder node meant to be replaced by a real one in the search
    best = Node(
        depth=depth,
        value=(VALUE_MAX + 1 if board.turn == COLOR.BLACK else -VALUE_MAX - 1),
    )

    # count the number of children (direct and non direct)
    # for info purposes
    children = 0

    smart_moves = []
    for move in board.pseudo_legal_moves():
        curr_board = board.copy()
        curr_board.push(move)
        node = engine.hashtable.get(curr_board.hash(), depth)
        if node is not None:
            curr_eval = node.value
        else:
            curr_eval = eval_board(curr_board)
        smart_moves.append(SmartMove(move=move, board=curr_board, eval=curr_eval))

    for smart_move in sorted(smart_moves, key=lambda x: x.eval, reverse=True):
        curr_pv = deque(pv)
        curr_pv.append(smart_move.move)
        node = alphabeta_tt_mo(smart_move.board, alpha, beta, depth - 1, curr_pv)
        children += node.children + 1

        # Save the resulting best node in the transposition table
        if node.depth > 0:
            engine.hashtable.add(smart_move.board.hash(), node)

        if board.turn == COLOR.WHITE:
            if node.value > best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                )
            alpha = max(alpha, node.value)
            if node.value >= beta:
                break
        else:
            if node.value < best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                )
            beta = min(beta, node.value)
            if node.value <= alpha:
                break

    # Save the resulting best node in the transposition table
    if best.depth > 0:
        engine.hashtable.add(board.hash(), best)

    return Node(
        value=best.value,
        depth=best.depth,
        pv=best.pv,
        children=children,
    )


# alphabeta pruning (fail-soft) with move ordering
def alphabeta_mo(board: Board, alpha: int, beta: int, depth: int, pv: deque) -> Node:

    # we check if there's no king of our color
    # in that case we can stop there
    if len(board.pieces[PIECE.KING * board.turn]) == 0:
        return Node(
            value=-VALUE_MAX * board.turn,
            depth=depth,
            pv=pv,
        )

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return Node(
            value=eval_board(board),
            depth=0,
            pv=pv,
        )

    # placeholder node meant to be replaced by a real one in the search
    best = Node(
        depth=depth,
        value=(VALUE_MAX + 1 if board.turn == COLOR.BLACK else -VALUE_MAX - 1),
    )

    # count the number of children (direct and non direct)
    # for info purposes
    children = 0

    smart_moves = []
    for move in board.pseudo_legal_moves():
        curr_board = board.copy()
        curr_board.push(move)
        # node = engine.hashtable.get(curr_board.hash(), depth)
        # curr_eval = eval_board(curr_board)
        smart_moves.append(
            SmartMove(move=move, board=curr_board, eval=move_eval(board, move))
        )

    ordered_smart_moves = sorted(smart_moves, key=lambda x: x.eval, reverse=True)

    for smart_move in ordered_smart_moves:
        curr_pv = deque(pv)
        curr_pv.append(smart_move.move)
        node = alphabeta_mo(smart_move.board, alpha, beta, depth - 1, curr_pv)
        children += node.children + 1

        if board.turn == COLOR.WHITE:
            if node.value > best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                )
            alpha = max(alpha, node.value)
            if node.value >= beta:
                break
        else:
            if node.value < best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                )
            beta = min(beta, node.value)
            if node.value <= alpha:
                break

    return Node(
        value=best.value,
        depth=best.depth,
        pv=best.pv,
        children=children,
    )


# simple alphabeta pruning (fail-soft) with transposition table
# not fully validated
def alphabeta_tt(board: Board, alpha: int, beta: int, depth: int, pv: deque) -> Node:

    if __debug__:
        global NODE_DEPTH
        NODE_DEPTH[depth] += 1

    # we check if there's no king of our color
    # in that case we can stop there
    if len(board.pieces[PIECE.KING * board.turn]) == 0:
        return Node(
            value=-VALUE_MAX * board.turn,
            depth=depth,
            pv=pv,
        )

    # check if we find a hit in the transposition table
    node = engine.hashtable.get(board.hash(), depth)
    if node is not None:
        if node.depth >= depth:
            # if node.depth == depth: # to reproduce pvs of other lower-end algs
            return Node(
                value=node.value,
                pv=pv,
                depth=node.depth,
            )

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return Node(
            value=eval_board(board),
            depth=0,
            pv=pv,
        )

    # placeholder node meant to be replaced by a real one in the search
    best = Node(
        depth=depth,
        value=(VALUE_MAX + 1 if board.turn == COLOR.BLACK else -VALUE_MAX - 1),
    )

    # count the number of children (direct and non direct)
    # for info purposes
    children = 0

    for move in board.pseudo_legal_moves():
        curr_board = board.copy()
        curr_board.push(move)
        curr_pv = deque(pv)
        curr_pv.append(move)
        node = alphabeta_tt(curr_board, alpha, beta, depth - 1, curr_pv)
        children += node.children + 1

        if board.turn == COLOR.WHITE:
            if node.value > best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                )
            alpha = max(alpha, node.value)
            if node.value >= beta:
                break
        else:
            if node.value < best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                )
            beta = min(beta, node.value)
            if node.value <= alpha:
                break

    # Save the resulting best node in the transposition table
    if best.depth > 0:
        engine.hashtable.add(board.hash(), best)

    return Node(
        value=best.value,
        depth=best.depth,
        pv=best.pv,
        children=children,
    )


# simple alphabeta pruning (fail-soft)
def alphabeta(board: Board, alpha: int, beta: int, depth: int, pv: deque) -> Node:

    # we check if there's no king of our color
    # in that case we can stop there
    if len(board.pieces[PIECE.KING * board.turn]) == 0:
        return Node(
            value=-VALUE_MAX * board.turn,
            depth=depth,
            pv=pv,
        )

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return Node(
            value=eval_board(board),
            depth=0,
            pv=pv,
        )

    # placeholder node meant to be replaced by a real one in the search
    best = Node(
        depth=depth,
        value=(VALUE_MAX + 1 if board.turn == COLOR.BLACK else -VALUE_MAX - 1),
    )

    # count the number of children (direct and non direct)
    # for info purposes
    children = 0

    for move in board.pseudo_legal_moves():
        curr_board = board.copy()
        curr_board.push(move)
        curr_pv = deque(pv)
        curr_pv.append(move)
        node = alphabeta(curr_board, alpha, beta, depth - 1, curr_pv)
        children += node.children + 1

        if board.turn == COLOR.WHITE:
            if node.value > best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                )
            alpha = max(alpha, node.value)
            if node.value >= beta:
                break
        else:
            if node.value < best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                )
            beta = min(beta, node.value)
            if node.value <= alpha:
                break

    return Node(
        value=best.value,
        depth=best.depth,
        pv=best.pv,
        children=children,
    )


# Simple minimax with transposition table
# not validated
def minimax_tt(board: Board, depth: int, pv: deque) -> Node:

    if __debug__:
        global NODE_DEPTH
        NODE_DEPTH[depth] += 1

    # we check if there's no king of our color
    # in that case we can stop there
    if len(board.pieces[PIECE.KING * board.turn]) == 0:
        return Node(
            value=-VALUE_MAX * board.turn,
            depth=depth,
            pv=pv,
            squares=board.squares,
        )

    # check if we find a hit in the transposition table
    node = engine.hashtable.get(board.hash(), depth)
    if node is not None:
        if node.depth >= depth:
            # if node.depth == depth: # to reproduce pvs of other lower-end algs
            if board.squares.tobytes() != node.squares.tobytes():
                global COLLISIONS
                COLLISIONS += 1
            return Node(
                value=node.value,
                pv=pv,
                depth=node.depth,
                squares=node.squares,
            )

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return Node(
            value=eval_board(board),
            depth=0,
            pv=pv,
            squares=board.squares,
        )

    # placeholder node meant to be replaced by a real one in the search
    best = Node(
        depth=depth,
        value=(VALUE_MAX + 1 if board.turn == COLOR.BLACK else -VALUE_MAX - 1),
    )

    # count the number of children (direct and non direct)
    # for info purposes
    children = 0

    for move in board.pseudo_legal_moves():
        curr_board = board.copy()
        curr_board.push(move)
        curr_pv = deque(pv)
        curr_pv.append(move)
        node = minimax_tt(curr_board, depth - 1, curr_pv)
        children += node.children + 1

        if board.turn == COLOR.WHITE:
            if node.value > best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                    squares=board.squares,
                )
        else:
            if node.value < best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                    squares=board.squares,
                )

    # Save the resulting best node in the transposition table
    if depth > 0:
        engine.hashtable.add(board.hash(), best)

    return Node(
        value=best.value,
        depth=best.depth,
        pv=best.pv,
        children=children,
    )


# Simple minimax
def minimax(board: Board, depth: int, pv: deque) -> Node:

    # we check if there's no king of our color
    # in that case we can stop there
    if len(board.pieces[PIECE.KING * board.turn]) == 0:
        return Node(
            value=-VALUE_MAX * board.turn,
            depth=depth,
            pv=pv,
        )

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return Node(
            value=eval_board(board),
            depth=0,
            pv=pv,
        )

    # placeholder node meant to be replaced by a real one in the search
    best = Node(
        depth=depth,
        value=(VALUE_MAX + 1 if board.turn == COLOR.BLACK else -VALUE_MAX - 1),
    )

    # count the number of children (direct and non direct)
    # for info purposes
    children = 0

    for move in board.pseudo_legal_moves():
        curr_board = board.copy()
        curr_board.push(move)
        curr_pv = deque(pv)
        curr_pv.append(move)
        node = minimax(curr_board, depth - 1, curr_pv)
        children += node.children + 1
        if board.turn == COLOR.WHITE:
            if node.value > best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                )
        else:
            if node.value < best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                )

    return Node(
        value=best.value,
        depth=best.depth,
        pv=best.pv,
        children=children,
    )
