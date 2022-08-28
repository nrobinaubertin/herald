"""
Search alogrithms

A "validated" algorithm is one that does give
the same result as minimax (with full pv equality)

_tt algorithms can be validated by only
taking tt_nodes with the same depth as the current pass
"""

from collections import deque
from .constants import COLOR, VALUE_MAX
from . import board
from .data_structures import Node, Board
from .transposition_table import TranspositionTable
from typing import Callable


# alphabeta pruning (fail-soft)
# with optional move ordering and transposition table
def alphabeta(
    b: Board,
    alpha: int,
    beta: int,
    depth: int,
    pv: deque,
    transposition_table: TranspositionTable | None = None,
    move_ordering_fn: Callable | None = None,
) -> Node:

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return Node(
            value=sum(b.eval, start=1),
            depth=0,
            pv=pv,
        )

    if transposition_table is not None:
        # check if we find a hit in the transposition table
        node = transposition_table.get(board.hash(b), depth)
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
        value=(VALUE_MAX + 1 if b.turn == COLOR.BLACK else -VALUE_MAX - 1),
    )

    # count the number of children (direct and non direct)
    # for info purposes
    children = 0

    for smart_move in (move_ordering_fn(b) if move_ordering_fn is not None else board.smart_moves(b)):
        curr_pv = deque(pv)
        curr_pv.append(smart_move.move)

        # return immediatly if this is a king capture
        if smart_move.move.is_king_capture:
            return Node(
                value=VALUE_MAX * b.turn,
                depth=depth,
                pv=pv,
            )

        node = alphabeta(
            smart_move.board,
            alpha,
            beta,
            depth - 1,
            curr_pv,
            transposition_table,
            move_ordering_fn
        )
        children += node.children + 1

        if b.turn == COLOR.WHITE:
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

    if transposition_table is not None:
        # Save the resulting best node in the transposition table
        if best.depth > 0:
            transposition_table.add(board.hash(b), best)

    return Node(
        value=best.value,
        depth=best.depth,
        pv=best.pv,
        children=children,
    )


# Simple minimax
def minimax(b: Board, depth: int, pv: deque) -> Node:

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return Node(
            value=sum(b.eval, start=1),
            depth=0,
            pv=pv,
        )

    # placeholder node meant to be replaced by a real one in the search
    best = Node(
        depth=depth,
        value=(VALUE_MAX + 1 if b.turn == COLOR.BLACK else -VALUE_MAX - 1),
    )

    # count the number of children (direct and non direct)
    # for info purposes
    children = 0

    for move in board.pseudo_legal_moves(b):
        curr_board = board.push(b, move)
        curr_pv = deque(pv)
        curr_pv.append(move)

        # return immediatly if this is a king capture
        if move.is_king_capture:
            return Node(
                value=VALUE_MAX * b.turn,
                depth=depth,
                pv=pv,
            )

        node = minimax(curr_board, depth - 1, curr_pv)
        children += node.children + 1
        if b.turn == COLOR.WHITE:
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
