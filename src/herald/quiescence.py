from collections import deque

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

            # if this is a cut-node
            if node.value >= node.upper:
                alpha = max(alpha, node.value)

            # if this is an all-node
            if node.value <= node.lower:
                beta = min(beta, node.value)

    # stand_pat evaluation to check if we stop QS
    stand_pat: int = config.eval_fn(b)
    if b.turn == COLOR.WHITE:
        # if stand_pat >= beta:
        #     # print("stand_pat", stand_pat, beta, to_uci(pv))
        #     return Node(
        #         value=beta,
        #         depth=0,
        #         full_move=b.full_move,
        #         pv=pv,
        #         lower=alpha,
        #         upper=beta,
        #         children=1,
        #     )
        alpha = max(alpha, stand_pat)
    else:
        # if stand_pat <= alpha:
        #     # print("stand_pat", to_uci(pv))
        #     return Node(
        #         value=alpha,
        #         depth=0,
        #         full_move=b.full_move,
        #         pv=pv,
        #         lower=alpha,
        #         upper=beta,
        #         children=1,
        #     )
        beta = min(beta, stand_pat)

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
                pv=curr_pv,
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
        # this happens when no quiescent move is available
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

    return node
