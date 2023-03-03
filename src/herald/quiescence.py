from . import board, pruning, move_ordering
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
        1,
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
    tactical_quota: int,
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

    # # the qs_tt is not so strict as the main tt
    # # so that it's faster.
    # if config.use_transposition_table:
    #     # check if we find a hit in the transposition table
    #     node = config.transposition_table.get(b, depth)
    #     # we don't check for depth in qs search. Everything goes in.
    #     if isinstance(node, Node):
    #         # we return the node instantly with bound checking.
    #         # return node
    #         return Node(
    #             value=node.value,
    #             depth=depth,
    #             pv=node.pv,
    #             lower=max(node.lower, alpha),
    #             upper=min(node.upper, beta),
    #             children=1,
    #         )
    #         # # first we make sure that the retrieved node
    #         # # is in our alpha-beta range
    #         # if alpha < node.lower and node.upper < beta:
    #         #     # if this is a cut-node
    #         #     if node.value >= node.upper:
    #         #         alpha = max(alpha, node.value)

    #         #     # if this is an all-node
    #         #     if node.value <= node.lower:
    #         #         beta = min(beta, node.value)

    #         #     # if this is an exact node
    #         #     if node.lower < node.value < node.upper:
    #         #         return node

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
    moves = board.pseudo_legal_moves(b)

    if not we_are_in_check and tactical_quota < 1:
        moves = (move for move in moves if move.is_capture)
        moves = move_ordering.qs_ordering(b, moves)
    else:
        moves = config.move_ordering_fn(b, moves)

    for move in moves:

        # we allow everything if we are in check
        # if the move is a good capture, then it's alright anyway
        if (
            (move.is_capture and not pruning.is_bad_capture(b, move, with_see=True))
            or we_are_in_check
        ):
            nb = board.push(b, move)
        else:
            # we need to have some tactical quota left
            if tactical_quota < 1:
                continue
            # the only tactical move allowed for now
            # are moves that check ennemy king
            nb, will_check_the_king = board.will_check_the_king(b, move)
            if not will_check_the_king:
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
            # if we were in check or if it's a capture, then we don't reduce our tactical quota
            tactical_quota if move.is_capture or we_are_in_check else tactical_quota - 1,
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

    # if config.use_qs_transposition_table:
    #     # Save the resulting best node in the transposition table
    #     if best is not None:
    #         config.qs_transposition_table[b] = best

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
