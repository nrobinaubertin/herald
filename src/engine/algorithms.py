"""
Search alogrithms
"""

from collections import deque
from .constants import COLOR, VALUE_MAX
from . import board
from .data_structures import Node, Board, Move
from .move_ordering import Move_ordering_fn
from .transposition_table import TranspositionTable
from .evaluation import Eval_fn
from typing import Callable


Alg_fn = Callable[
    [
        Board,
        int,
        deque[Move],
        Eval_fn,
        int | None,
        int | None,
        TranspositionTable | None,
        Move_ordering_fn | None,
    ],
    Node
]


def negac(
    b: Board,
    depth: int,
    pv: deque[Move],
    eval_fn: Eval_fn,
    min: int,
    max: int,
    transposition_table: TranspositionTable | None = None,
    move_ordering_fn: Move_ordering_fn | None = None,
) -> Node:

    children: int = 0

    min_node: Node = Node(
        depth=depth,
        value=min
    )
    max_node: Node = Node(
        depth=depth,
        value=max,
    )
    current_node: Node = min_node

    # we seem to evaluate less node w/ this roughness value
    ROUGHNESS: int = 1000

    while min_node.value < max_node.value - ROUGHNESS:
        current_value = (min_node.value + max_node.value + 1) // 2
        current_node = alphabeta(
            b,
            depth,
            pv,
            eval_fn,
            current_value,
            current_value + 1,
            transposition_table,
            move_ordering_fn,
        )
        children += current_node.children
        if current_node.value > current_value:
            min_node = current_node
        if current_node.value <= current_value:
            max_node = current_node

    current_node = alphabeta(
        b,
        depth,
        pv,
        eval_fn,
        min_node.value - ROUGHNESS//2,
        max_node.value + ROUGHNESS//2,
        transposition_table,
        move_ordering_fn,
    )
    children += current_node.children

    return Node(
        value=current_node.value,
        depth=current_node.depth,
        pv=current_node.pv,
        full_move=current_node.full_move,
        children=children,
    )


# alphabeta pruning (fail-soft)
# with optional move ordering and transposition table
def alphabeta(
    b: Board,
    depth: int,
    pv: deque[Move],
    eval_fn: Eval_fn,
    alpha: int,
    beta: int,
    transposition_table: TranspositionTable | None = None,
    move_ordering_fn: Move_ordering_fn | None = None,
) -> Node:

    assert depth >= 0, depth

    if isinstance(transposition_table, TranspositionTable):
        # check if we find a hit in the transposition table
        node = transposition_table.get(b, depth)
        if isinstance(node, Node) and node.depth >= depth:
            # handle the found node as usual
            if b.turn == COLOR.WHITE:
                alpha = max(alpha, node.value)
                if node.value >= beta:
                    return Node(
                        value=node.value,
                        pv=node.pv,
                        depth=node.depth,
                        full_move=node.full_move,
                        lower=alpha,
                        upper=beta,
                        children=1,
                    )
            else:
                beta = min(beta, node.value)
                if node.value <= alpha:
                    return Node(
                        value=node.value,
                        pv=node.pv,
                        depth=node.depth,
                        full_move=node.full_move,
                        lower=alpha,
                        upper=beta,
                        children=1,
                    )

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return Node(
            value=eval_fn(b, alpha, beta, transposition_table, 0),
            depth=0,
            full_move=b.full_move,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=1,
        )

    # count the number of children (direct and non direct)
    # for info purposes
    children = 1

    # placeholder node meant to be replaced by a real one in the search
    best = Node(
        depth=depth,
        value=(VALUE_MAX + 1 if b.turn == COLOR.BLACK else -VALUE_MAX - 1),
        full_move=b.full_move,
        lower=alpha,
        upper=beta,
        children=children,
    )

    for move in (
        move_ordering_fn(b, transposition_table)
        if move_ordering_fn is not None
        else board.pseudo_legal_moves(b)
    ):
        curr_pv = deque(pv)
        curr_pv.append(move)

        # return immediatly if this is a king capture
        if move.is_king_capture:
            return Node(
                value=VALUE_MAX * b.turn,
                depth=depth,
                full_move=b.full_move,
                pv=pv,
                lower=alpha,
                upper=beta,
                children=children,
            )

        nb = board.push(b, move)
        node = alphabeta(
            nb,
            depth - 1,
            curr_pv,
            eval_fn,
            alpha,
            beta,
            transposition_table,
            move_ordering_fn
        )

        children += node.children

        if b.turn == COLOR.WHITE:
            if node.value > best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    full_move=node.full_move,
                    pv=node.pv,
                    lower=alpha,
                    upper=beta,
                    children=children,
                )
            alpha = max(alpha, node.value)
            if node.value >= beta:
                break
        else:
            if node.value < best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    full_move=node.full_move,
                    pv=node.pv,
                    lower=alpha,
                    upper=beta,
                    children=children,
                )
            beta = min(beta, node.value)
            if node.value <= alpha:
                break

    if isinstance(transposition_table, TranspositionTable):
        # Save the resulting best node in the transposition table
        if best.depth > 0:
            transposition_table.add(b, best)

    node = Node(
        value=best.value,
        depth=best.depth,
        pv=best.pv,
        full_move=best.full_move,
        children=children,
    )

    return node


# Simple minimax
def minimax(
    b: Board,
    depth: int,
    pv: deque[Move],
    eval_fn: Eval_fn,
    _1: int | None = None,
    _2: int | None = None,
    transposition_table: TranspositionTable | None = None,
    move_ordering_fn: Move_ordering_fn | None = None,
) -> Node:

    assert depth >= 0, depth

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return Node(
            value=eval_fn(b),
            depth=0,
            pv=pv,
            children=1,
        )

    # placeholder node meant to be replaced by a real one in the search
    best = Node(
        depth=depth,
        value=(VALUE_MAX + 1 if b.turn == COLOR.BLACK else -VALUE_MAX - 1),
        children=1,
    )

    # count the number of children (direct and non direct)
    # for info purposes
    children = 1

    for move in (
        move_ordering_fn(b, transposition_table)
        if move_ordering_fn is not None
        else board.pseudo_legal_moves(b)
    ):
        curr_board = board.push(b, move)
        curr_pv = deque(pv)
        curr_pv.append(move)

        # return immediatly if this is a king capture
        if move.is_king_capture:
            return Node(
                value=VALUE_MAX * b.turn,
                depth=depth,
                pv=pv,
                children=children,
            )

        node = minimax(
            curr_board,
            depth - 1,
            curr_pv,
            eval_fn
        )

        children += node.children

        if b.turn == COLOR.WHITE:
            if node.value > best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                    children=children,
                )
        else:
            if node.value < best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                    children=children,
                )

    return Node(
        value=best.value,
        depth=best.depth,
        pv=best.pv,
        children=children,
    )
