from collections import deque

from . import board, pruning
from .board import Board
from .configuration import Config
from .constants import COLOR, VALUE_MAX
from .data_structures import Move, Node


def quiescence(
    config: Config,
    b: Board,
    pv: deque[Move],
    alpha: int,
    beta: int,
) -> Node:
    node = _search(
        config,
        b,
        0,
        pv,
        alpha,
        beta,
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

    # if we are on a terminal node, return the evaluation
    if depth >= config.quiescence_depth:
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

    if depth < 2 and config.use_transposition_table:
        # check if we find a hit in the transposition table
        node = config.transposition_table.get(b, depth)
        if isinstance(node, Node) and node.depth >= depth:
            # if this is a cut-node
            if node.value >= node.upper:
                alpha = max(alpha, node.value)

            # if this is an all-node
            if node.value <= node.lower:
                beta = min(beta, node.value)

    # stand_pat evaluation to check if we stop QS
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

    # count the number of children (direct and non direct)
    # for info purposes
    children = 1

    best = None
    moves = board.pseudo_legal_moves(b, True)

    for move in moves:
        if pruning.is_bad_capture(b, move, with_see=True):
            continue

        curr_pv = deque(pv)
        curr_pv.append(move)

        # return immediately if this is a king capture
        if move.is_king_capture:
            return Node(
                value=VALUE_MAX * b.turn,
                depth=depth,
                full_move=b.full_move,
                pv=curr_pv,
                lower=alpha,
                upper=beta,
                children=children,
            )

        nb = board.push(b, move)

        # if the king is in check after we move
        # then it's a bad move (we will lose the game)
        if board.king_is_in_check(nb, nb.invturn):
            continue

        node = _search(
            config,
            nb,
            depth + 1,
            curr_pv,
            alpha,
            beta,
        )

        children += node.children

        if b.turn == COLOR.WHITE:
            if node.value >= alpha:
                if best is None or node.value > best.value:
                    best = Node(
                        value=node.value,
                        depth=0,
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
            if node.value <= beta:
                if best is None or node.value < best.value:
                    best = Node(
                        value=node.value,
                        depth=0,
                        full_move=node.full_move,
                        pv=node.pv,
                        lower=alpha,
                        upper=beta,
                        children=children,
                    )
                beta = min(beta, node.value)
                if node.value <= alpha:
                    break

    if best is not None:
        node = Node(
            value=best.value,
            depth=0,
            pv=best.pv,
            full_move=best.full_move,
            children=children,
        )
    else:
        # this happens when no quiescent move is available
        value = config.eval_fn(b)
        return Node(
            value=value,
            depth=0,
            full_move=b.full_move,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=children,
        )

    return node
