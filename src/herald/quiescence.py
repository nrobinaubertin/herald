from . import board, evaluation, pruning
from .board import Board
from .configuration import Config
from .constants import COLOR, COLOR_DIRECTION, VALUE_MAX
from .data_structures import Move, Node


def quiescence(
    config: Config,
    b: Board,
    pv: list[Move],
    alpha: int,
    beta: int,
    debug: bool = False,
) -> Node:
    node = _search(
        config=config,
        b=b,
        depth=0,
        pv=pv,
        alpha=alpha,
        beta=beta,
    )

    return Node(
        value=node.value,
        depth=0,
        pv=node.pv,
        lower=alpha,
        upper=beta,
        children=node.children,
    )


def _search(
    *,
    config: Config,
    b: Board,
    depth: int = 0,
    pv: list[Move],
    alpha: int,
    beta: int,
) -> Node:
    assert depth >= 0, depth

    # if we are on a terminal node, return the evaluation
    if depth >= config.quiescence_depth:
        value = evaluation.eval_fast(b.squares, b.remaining_material)
        return Node(
            value=value,
            depth=0,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=1,
        )

    # count the number of children (direct and non direct)
    # for info purposes
    children = 1

    we_are_in_check = board.is_square_attacked(b.squares, b.king_squares[b.turn], b.invturn)

    if not we_are_in_check:
        # stand_pat evaluation to check if we stop QS
        stand_pat: int = evaluation.eval_fast(b.squares, b.remaining_material)
        # if depth == 0:
        #     print(stand_pat)
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
        best = Node(
            value=stand_pat,
            depth=0,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=1,
        )
        moves = board.tactical_moves(b)
    else:
        best = None
        moves = board.pseudo_legal_moves(b)

    for move in moves:
        if not we_are_in_check:
            # if we are not evaluating a capture move
            # and if we found already something good
            # then we can skip the rest
            # (capture moves are generated first)
            if not move.is_capture and best is not None:
                break

            # skip bad capture moves
            if pruning.is_bad_capture(b, move):
                continue

        nb = board.push(b, move)

        # if the king is in check after we move
        # then it's a bad move (we will lose the game)
        if board.king_is_in_check(nb, nb.invturn):
            continue

        if __debug__:
            curr_pv = pv.copy()
            curr_pv.append(move)
        else:
            curr_pv = pv

        node = _search(
            config=config,
            b=nb,
            depth=depth + 1,
            pv=curr_pv,
            alpha=alpha,
            beta=beta,
        )

        children += node.children

        if b.turn == COLOR.WHITE:
            if best is None or node.value > best.value:
                # if depth == 0:
                #     print(best, node)
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
            if best is None or node.value < best.value:
                # if depth == 0:
                #     print(best, node)
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
        # if the king square is attacked and we have no moves, it's a mate
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
            value = evaluation.eval_fast(b.squares, b.remaining_material)
            return Node(
                value=value,
                depth=0,
                pv=pv,
                lower=alpha,
                upper=beta,
                children=children,
            )

    return node
