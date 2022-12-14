from collections import deque
from .constants import COLOR, VALUE_MAX
from . import board
from .data_structures import Node, Board, Move, MoveType, to_uci
from .move_ordering import Move_ordering_fn, no_ordering
from .transposition_table import TranspositionTable
from .evaluation import Eval_fn
from typing import Callable


def quiescence(
    b: Board,
    depth: int,
    pv: deque[Move],
    eval_fn: Eval_fn,
    alpha: int,
    beta: int,
    transposition_table: TranspositionTable | None = None,
    move_ordering_fn: Move_ordering_fn = no_ordering,
    move_type: MoveType = MoveType.PSEUDO_LEGAL,
) -> Node:
    stand_pat: int = eval_fn(b, transposition_table)

    # if we are already in a quiescent search,
    # that means that we have hit the quiescent depth limit
    if move_type == MoveType.QUIESCENT:
        # print(f"{','.join([to_uci(x) for x in pv])}")
        return Node(
            value=stand_pat,
            depth=0,
            full_move=b.full_move,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=1,
        )

    value = stand_pat

    if b.turn == COLOR.WHITE:
        if value >= beta:
            return Node(
                value=beta,
                depth=0,
                full_move=b.full_move,
                pv=pv,
                lower=alpha,
                upper=beta,
                children=1,
            )
        alpha = max(alpha, value)
    else:
        if value <= alpha:
            return Node(
                value=alpha,
                depth=0,
                full_move=b.full_move,
                pv=pv,
                lower=alpha,
                upper=beta,
                children=1,
            )
        beta = min(beta, value)

    node = _search(
        b,
        depth,
        pv,
        eval_fn,
        alpha,
        beta,
        transposition_table,
        move_ordering_fn,
        MoveType.QUIESCENT,
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
    b: Board,
    depth: int,
    pv: deque[Move],
    eval_fn: Eval_fn,
    alpha: int,
    beta: int,
    transposition_table: TranspositionTable | None = None,
    move_ordering_fn: Move_ordering_fn = no_ordering,
    move_type: MoveType = MoveType.PSEUDO_LEGAL,
) -> Node:

    assert depth >= 0, depth

    if board.to_fen(b) == "r3k2r/pbpp2pp/3bpn2/2P5/3P4/4P2q/PP3PP1/RN1Q1RK1 w kq - 0 14":
        breakpoint()

    # test repetitions by returning it as a draw
    if move_type != MoveType.QUIESCENT and board.get_pos(b) in b.positions_history:
        return Node(
            value=0,
            depth=0,
            full_move=b.full_move,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=1,
        )

    # test repetitions of null move in quiescence search
    if (
        move_type == MoveType.QUIESCENT
        and (
            b.moves_history[-1].is_null_move
            and b.moves_history[-2].is_null_move
        )
    ):
        return Node(
            value=eval_fn(b, transposition_table),
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

    # if we are on a terminal node, return the evaluation
    if depth == 0:

        stand_pat: int = eval_fn(b, transposition_table)

        # if we are already in a quiescent search,
        # that means that we have hit the quiescent depth limit
        if move_type == MoveType.QUIESCENT:
            # print(f"{','.join([to_uci(x) for x in pv])}")
            return Node(
                value=stand_pat,
                depth=0,
                full_move=b.full_move,
                pv=pv,
                lower=alpha,
                upper=beta,
                children=1,
            )

        value = stand_pat

        if b.turn == COLOR.WHITE:
            if value >= beta:
                return Node(
                    value=beta,
                    depth=0,
                    full_move=b.full_move,
                    pv=pv,
                    lower=alpha,
                    upper=beta,
                    children=1,
                )
            alpha = max(alpha, value)
        else:
            if value <= alpha:
                return Node(
                    value=alpha,
                    depth=0,
                    full_move=b.full_move,
                    pv=pv,
                    lower=alpha,
                    upper=beta,
                    children=1,
                )
            beta = min(beta, value)

        QUIESCENT_DEPTH: int = 20
        node = _search(
            b,
            QUIESCENT_DEPTH,
            pv,
            eval_fn,
            alpha,
            beta,
            transposition_table,
            move_ordering_fn,
            MoveType.QUIESCENT,
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

    # count the number of children (direct and non direct)
    # for info purposes
    children = 1

    best = None

    # if len(move_ordering_fn(b, transposition_table, move_type)) == 0:
    #     print(board.to_fen(b))

    for move in move_ordering_fn(b, transposition_table, move_type):
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
        if best is not None and best.depth > 0 and move_type != MoveType.QUIESCENT:
            transposition_table.add(b, best)

    if best is not None:
        node = Node(
            value=best.value,
            depth=best.depth,
            pv=best.pv,
            full_move=best.full_move,
            children=children,
        )
    else:
        # breakpoint()
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
