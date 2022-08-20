"""
Search alogrithms
A "validated" algorithm is one that does give the same result as minimax (with full pv equality)
_tt algorithms can be validated by only taking tt_nodes with the same depth as the current pass
"""

from collections import deque, namedtuple
from .constants import PIECE, COLOR
from .evaluation import VALUE_MAX, eval_board, move_eval
from .board import Board
from .data_structures import Node
from .transposition_table import TranspositionTable

SmartMove = namedtuple("SmartMove", ["move", "board", "eval"])


# alphabeta pruning (fail-soft) with move ordering and transposition table
def alphabeta_mo_tt(
    board: Board,
    alpha: int,
    beta: int,
    depth: int,
    pv: deque,
    transposition_table: TranspositionTable,
) -> Node:

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
    node = transposition_table.get(board.hash(), depth)
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
        # node = tt.get(curr_board.hash(), depth)
        # curr_eval = eval_board(curr_board)
        smart_moves.append(
            SmartMove(move=move, board=curr_board, eval=move_eval(board, move))
        )

    ordered_smart_moves = sorted(smart_moves, key=lambda x: x.eval, reverse=True)

    for smart_move in ordered_smart_moves:
        curr_pv = deque(pv)
        curr_pv.append(smart_move.move)
        node = alphabeta_mo_tt(
            smart_move.board, alpha, beta, depth - 1, curr_pv, transposition_table
        )
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
        transposition_table.add(board.hash(), best)

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
