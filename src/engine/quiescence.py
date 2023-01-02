from collections import deque
from typing import Iterable

from . import board
from .configuration import Config
from .constants import COLOR, VALUE_MAX
from .data_structures import Board, Move, Node
from .pruning import is_bad_capture


def quiescence(
    config: Config,
    b: Board,
    depth: int,
    pv: deque[Move],
    alpha: int,
    beta: int,
) -> Node:
    stand_pat: int = config.eval_fn(b)

    if b.turn == COLOR.WHITE:
        if stand_pat >= beta:
            return Node(
                value=beta,
                depth=0,
                full_move=b.full_move,
                pv=pv,
                lower=alpha,
                upper=beta,
                children=1,
            )
        alpha = max(alpha, stand_pat)
    else:
        if stand_pat <= alpha:
            return Node(
                value=alpha,
                depth=0,
                full_move=b.full_move,
                pv=pv,
                lower=alpha,
                upper=beta,
                children=1,
            )
        beta = min(beta, stand_pat)

    node = _search(
        config,
        b,
        depth,
        pv,
        -VALUE_MAX,
        VALUE_MAX,
    )

    return Node(
        value=node.value,
        depth=0,
        full_move=b.full_move,
        pv=node.pv,
        lower=alpha,
        upper=beta,
        children=node.children,
    )


def _search(
    config: Config,
    b: Board,
    depth: int,
    pv: deque[Move],
    alpha: int,
    beta: int,
) -> Node:

    assert depth >= 0, depth

    if config.use_qs_transposition_table:
        # check if we find a hit in the transposition table
        node = config.qs_transposition_table.get(b, depth)
        if isinstance(node, Node) and node.depth >= depth:

            # exact node
            if node.lower < node.value < node.upper:
                return Node(
                    value=node.value,
                    pv=pv,
                    depth=node.depth,
                    full_move=node.full_move,
                    lower=alpha,
                    upper=beta,
                    children=1,
                )

            # if this is a cut-node
            if node.value >= node.upper:
                alpha = max(alpha, node.value)

            # if this is an all-node
            if node.value <= node.lower:
                beta = min(beta, node.value)

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        value = config.eval_fn(b)
        return Node(
            value=value,
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

    best = None
    moves = board.pseudo_legal_moves(b, True)
    if depth > 1:
        moves = filter(lambda x: not is_bad_capture(b, x, with_see=True), moves)
    else:
        moves = filter(lambda x: not is_bad_capture(b, x, with_see=False), moves)
    for move in config.qs_move_ordering_fn(b, moves):
        curr_pv = deque(pv)
        curr_pv.append(move)

        # return immediately if this is a king capture
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

        if move.is_null:
            # don't go further if this is a null move
            value = config.eval_fn(b)
            node = Node(
                value=value,
                depth=depth,
                full_move=b.full_move,
                pv=pv,
                lower=alpha,
                upper=beta,
                children=1,
            )
        else:
            nb = board.push(b, move)
            node = _search(
                config,
                nb,
                depth - 1,
                curr_pv,
                alpha,
                beta,
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

    if config.use_qs_transposition_table:
        # Save the resulting best node in the transposition table
        if best is not None and best.depth > 0:
            config.qs_transposition_table.add(b, best)

    if best is not None:
        node = Node(
            value=best.value,
            depth=best.depth,
            pv=best.pv,
            full_move=best.full_move,
            children=children,
        )
    else:
        # no "best" found
        node = Node(
            depth=depth,
            value=config.eval_fn(b),
            pv=pv,
            full_move=b.full_move,
            lower=alpha,
            upper=beta,
            children=children,
        )

    return node
