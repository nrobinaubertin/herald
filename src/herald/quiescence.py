from . import board, pruning
from .board import Board
from .configuration import Config
from .constants import COLOR, COLOR_DIRECTION, VALUE_MAX
from .data_structures import Move, Node, to_uci


def quiescence(
    config: Config,
    b: Board,
    pv: list[Move],
    alpha: int,
    beta: int,
    debug: bool = False,
) -> Node:
    node = _search(
        config,
        b,
        0,
        pv,
        alpha,
        beta,
        2,
    )

    if debug:
        print([node.value] + [to_uci(m) for m in node.pv])

    return Node(
        value=node.value,
        depth=0,
        pv=node.pv,
        lower=alpha,
        upper=beta,
        children=node.children,
    )


def _search(
    config: Config,
    b: Board,
    depth: int,
    pv: list[Move],
    alpha: int,
    beta: int,
    check_quota: int,
) -> Node:
    assert depth >= 0, depth

    # if we are on a terminal node, return the evaluation
    if depth >= config.quiescence_depth:
        value = config.eval_fn(b)
        return Node(
            value=value,
            depth=0,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=1,
        )

    if depth < 2 and config.use_transposition_table:
        # check if we find a hit in the transposition table
        node = config.transposition_table.get(b, depth)
        if isinstance(node, Node) and node.depth >= depth:
            # first we make sure that the retrieved node
            # is in our alpha-beta range
            if alpha < node.lower and node.upper < beta:
                # if this is a cut-node
                if node.value >= node.upper:
                    alpha = max(alpha, node.value)

                # if this is an all-node
                if node.value <= node.lower:
                    beta = min(beta, node.value)

                # if this is an exact node
                if node.lower < node.value < node.upper:
                    return node

    # count the number of children (direct and non direct)
    # for info purposes
    children = 1

    best = None
    we_are_in_check = board.is_square_attacked(b.squares, b.king_squares[b.turn], b.invturn)

    if not we_are_in_check:
        # stand_pat evaluation to check if we stop QS
        stand_pat: int = config.eval_fn(b)
        if b.turn == COLOR.WHITE:
            if stand_pat >= beta:
                return Node(
                    value=beta,
                    depth=0,
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
                    pv=pv,
                    lower=alpha,
                    upper=beta,
                    children=1,
                )
            beta = min(beta, stand_pat)

    for move in board.pseudo_legal_moves(b):
        if check_quota > 0:
            nb, will_check_the_king = board.will_check_the_king(b, move)
            if not we_are_in_check:
                if not will_check_the_king:
                    if pruning.is_bad_capture(b, move, with_see=True):
                        continue
                    if not move.is_capture:
                        continue
                else:
                    if check_quota < 1:
                        continue
                    check_quota -= 1
        else:
            nb = board.push(b, move)
            if not we_are_in_check:
                if pruning.is_bad_capture(b, move, with_see=True):
                    continue
                if not move.is_capture:
                    continue

        curr_pv = pv.copy()
        curr_pv.append(move)

        # return immediately if this is a king capture
        if move.is_king_capture:
            return Node(
                value=VALUE_MAX * b.turn,
                depth=depth,
                pv=curr_pv,
                lower=alpha,
                upper=beta,
                children=children,
            )

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
            check_quota,
        )

        children += node.children

        if b.turn == COLOR.WHITE:
            if node.value >= alpha or we_are_in_check:
                if best is None or node.value > best.value:
                    best = Node(
                        value=node.value,
                        depth=0,
                        pv=node.pv,
                        lower=alpha,
                        upper=beta,
                        children=children,
                    )
                alpha = max(alpha, node.value)
                if node.value >= beta:
                    break
        else:
            if node.value <= beta or we_are_in_check:
                if best is None or node.value < best.value:
                    best = Node(
                        value=node.value,
                        depth=0,
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
            children=children,
        )
    else:
        # this happens when no quiescent move is available
        if board.is_square_attacked(b.squares, b.king_squares[b.turn], b.invturn):
            node = Node(
                depth=depth,
                value=VALUE_MAX * COLOR_DIRECTION[b.turn] * -1,
                pv=pv,
                lower=alpha,
                upper=beta,
                children=children,
            )
        else:
            value = config.eval_fn(b)
            return Node(
                value=value,
                depth=0,
                pv=pv,
                lower=alpha,
                upper=beta,
                children=children,
            )

    return node
