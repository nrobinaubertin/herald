"""
Search alogrithms
"""

from collections import deque
from .constants import COLOR, VALUE_MAX
from . import board
from .data_structures import Node, Board, Move, MoveType
from .move_ordering import Move_ordering_fn, no_ordering
from .transposition_table import TranspositionTable
from .evaluation import Eval_fn
from .quiescence import quiescence
from typing import Callable, Iterable


Alg_fn = Callable[
    [
        Board,
        int,
        deque[Move],
        Eval_fn,
        int | None,
        int | None,
        TranspositionTable | None,
        Move_ordering_fn,
        MoveType,
        dict,
    ],
    Node
]


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
    move_ordering_fn: Move_ordering_fn = no_ordering,
    move_type: MoveType = MoveType.PSEUDO_LEGAL,
    options: dict = {},
) -> Node:

    assert depth >= 0, depth

    # test repetitions by returning it as a draw
    if board.get_pos(b) in b.positions_history:
        return Node(
            value=0,
            depth=0,
            full_move=b.full_move,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=1,
        )

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

    # count the number of children (direct and non direct)
    # for info purposes
    children: int = 1

    # if we are on a terminal node, return the evaluation
    if depth == 0:

        value: int = 0
        if options.get("quiescence_search", False):
            node = quiescence(
                b,
                options.get("quiescence_depth", 0),
                pv,
                eval_fn,
                alpha,
                beta,
                transposition_table,
                move_ordering_fn,
                MoveType.QUIESCENT,
            )

            children = node.children
            value = node.value
            pv = node.pv
        else:
            value = eval_fn(b, transposition_table)

        return Node(
            value=value,
            depth=0,
            full_move=b.full_move,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=children,
        )

    best = None

    moves: Iterable[Move] = []
    if move_type == MoveType.PSEUDO_LEGAL:
        moves = board.pseudo_legal_moves(b)
    if move_type == MoveType.LEGAL:
        moves = board.legal_moves(b)
    for move in move_ordering_fn(b, moves, transposition_table):
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
            move_ordering_fn,
            MoveType.PSEUDO_LEGAL if move_type == MoveType.LEGAL else move_type,
        )

        children += node.children

        if b.turn == COLOR.WHITE:
            if best is None or node.value > best.value:
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
            if best is None or node.value < best.value:
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
        if best is not None and best.depth > 0:
            transposition_table.add(b, best)

    if best is not None:
        node = Node(
            depth=best.depth,
            value=best.value,
            pv=best.pv,
            full_move=best.full_move,
            lower=alpha,
            upper=beta,
            children=children,
        )
    else:
        # no "best" found
        node = Node(
            depth=depth,
            value=eval_fn(b, transposition_table),
            pv=pv,
            full_move=b.full_move,
            lower=alpha,
            upper=beta,
            children=children,
        )

    return node


# Simple minimax
def minimax(
    b: Board,
    depth: int,
    pv: deque[Move],
    eval_fn: Eval_fn,
    alpha: int | None = None,
    beta: int | None = None,
    transposition_table: TranspositionTable | None = None,
    move_ordering_fn: Move_ordering_fn = no_ordering,
    move_type: MoveType = MoveType.PSEUDO_LEGAL,
    options: dict = {},
) -> Node:

    assert depth >= 0, depth

    # test repetitions by returning it as a draw
    if board.get_pos(b) in b.positions_history:
        return Node(
            value=0,
            depth=0,
            full_move=b.full_move,
            pv=pv,
            children=1,
        )

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return Node(
            value=eval_fn(b, transposition_table),
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

    moves: Iterable[Move] = []
    if move_type == MoveType.PSEUDO_LEGAL:
        moves = board.pseudo_legal_moves(b)
    if move_type == MoveType.LEGAL:
        moves = board.legal_moves(b)
    for move in move_ordering_fn(b, moves, transposition_table):
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
            eval_fn,
            None,
            None,
            transposition_table,
            move_ordering_fn,
            MoveType.PSEUDO_LEGAL if move_type == MoveType.LEGAL else move_type,
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
