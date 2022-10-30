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
from .data_structures import Node, Board, Move
from .move_ordering import Move_ordering_fn
from .transposition_table import TranspositionTable


def negac(
    b: Board,
    min: int,
    max: int,
    depth: int,
    pv: deque[Move],
    transposition_table: TranspositionTable | None = None,
    move_ordering_fn: Move_ordering_fn | None = None,
) -> Node:

    min_node = Node(
        depth=depth,
        value=min
    )
    max_node = Node(
        depth=depth,
        value=max,
    )

    current_node = None

    while abs(min_node.value - max_node.value) > 99:
        current_value = (min_node.value + max_node.value) // 2
        node = alphabeta(
            b,
            current_value - 50,
            current_value + 50,
            depth,
            pv,
            transposition_table,
            move_ordering_fn,
        )
        current_node = node
        if current_node.value > current_value:
            min_node = current_node
        else:
            max_node = current_node
        # print(f"{current_node.value} [{current_value}, {min_node.value}, {max_node.value}]")

    current_value = (min_node.value + max_node.value) // 2
    node = alphabeta(
        b,
        current_value - 50,
        current_value + 50,
        depth,
        pv,
        transposition_table,
        move_ordering_fn,
    )
    current_node = node

    return current_node


def aspiration_window(
    b: Board,
    guess: int,
    depth: int,
    pv: deque[Move],
    transposition_table: TranspositionTable | None = None,
    move_ordering_fn: Move_ordering_fn | None = None,
) -> Node:

    lower = guess - 50
    upper = guess + 50
    iteration = 0

    # count the number of children (direct and non direct)
    # for info purposes
    children = 0

    while True:
        iteration += 1
        # assert len(pv) != 0, "There should be a least a move in pv"
        node = alphabeta(
            b,
            lower,
            upper,
            depth,
            pv,
            transposition_table,
            move_ordering_fn,
        )
        children += node.children + 1
        if node.value >= upper:
            upper += 100 * (iteration**2)
            continue
        if node.value <= lower:
            lower -= 100 * (iteration**2)
            continue
        break

    if __debug__ and depth > 4 and transposition_table is not None:
        print(transposition_table.stats())

    return Node(
        value=node.value,
        depth=node.depth,
        pv=node.pv,
        full_move=node.full_move,
        children=children,
    )


# alphabeta pruning (fail-soft)
# with optional move ordering and transposition table
def alphabeta(
    b: Board,
    alpha: int,
    beta: int,
    depth: int,
    pv: deque[Move],
    transposition_table: TranspositionTable | None = None,
    move_ordering_fn: Move_ordering_fn | None = None,
) -> Node:

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return Node(
            value=sum(b.eval, start=1),
            depth=0,
            full_move=b.full_move,
            pv=pv,
        )

    if transposition_table is not None:
        # check if we find a hit in the transposition table
        node = transposition_table.get(b, depth)
        if node is not None:
            new_pv = node.pv.copy()
            new_pv.popleft()  # remove first move as it's the same as last of pv
            return Node(
                value=node.value,
                pv=pv + node.pv,
                depth=node.depth,
                full_move=node.full_move,
            )

    # placeholder node meant to be replaced by a real one in the search
    best = Node(
        depth=depth,
        value=(VALUE_MAX + 1 if b.turn == COLOR.BLACK else -VALUE_MAX - 1),
        full_move=b.full_move,
    )

    # count the number of children (direct and non direct)
    # for info purposes
    children = 0

    for smart_move in (
        move_ordering_fn(b, transposition_table)
        if move_ordering_fn is not None
        else board.smart_moves(b)
    ):
        curr_pv = deque(pv)
        curr_pv.append(smart_move.move)

        # return immediatly if this is a king capture
        if smart_move.move.is_king_capture:
            return Node(
                value=VALUE_MAX * b.turn,
                depth=depth,
                full_move=b.full_move,
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
                    full_move=node.full_move,
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
                    full_move=node.full_move,
                    pv=node.pv,
                )
            beta = min(beta, node.value)
            if node.value <= alpha:
                break

    if transposition_table is not None:
        # Save the resulting best node in the transposition table
        if best.depth > 0:
            transposition_table.add(b, best)

    return Node(
        value=best.value,
        depth=best.depth,
        pv=best.pv,
        full_move=best.full_move,
        children=children,
    )


# Simple minimax
def minimax(b: Board, depth: int, pv: deque[Move]) -> Node:

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
