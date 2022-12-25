from collections import deque
from .constants import COLOR, VALUE_MAX
from . import board
from .data_structures import Node, Board, Move
from typing import Iterable
from .pruning import is_bad_capture
from .configuration import Config


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

    # test null move in quiescence search
    if (
        b.moves_history[-1].is_null
    ):
        value = config.eval_fn(b)
        return Node(
            value=value,
            depth=depth,
            full_move=b.full_move,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=1,
        )

    if config.use_qs_transposition_table:
        # check if we find a hit in the transposition table
        node = config.qs_transposition_table.get(b, depth)
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

    moves: Iterable[Move] = [
        x for x in board.pseudo_legal_moves(b, True)
        if not is_bad_capture(b, x)
    ]
    for move in config.move_ordering_fn(b, moves):
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
