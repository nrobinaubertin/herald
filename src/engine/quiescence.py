from collections import deque
from .constants import COLOR, VALUE_MAX, PIECE
from . import board
from .data_structures import Node, Board, Move, MoveType, to_uci
from .move_ordering import Move_ordering_fn, no_ordering
from .transposition_table import TranspositionTable
from .evaluation import Eval_fn, PIECE_VALUE
from typing import Iterable


def is_bad_capture(b: Board, move: Move) -> bool:

    # a non-capture move is not a bad capture
    if not move.is_capture:
        return False

    piece_start = b.squares[move.start]

    if abs(piece_start) == PIECE.PAWN or abs(piece_start) == PIECE.KING:
        return False

    # captured piece is worth more than capturing piece
    if PIECE_VALUE[abs(b.squares[move.end])] >= PIECE_VALUE[abs(b.squares[move.start])] - 50:
        return False

    # if the piece is defended by a pawn, then it's a bad capture
    for depl in [9, 11] if b.turn == COLOR.WHITE else [-9, -11]:
        if (
            abs(b.squares[move.start + depl]) == PIECE.PAWN
            and b.squares[move.start + depl] * b.turn < 0
        ):
            return True

    # if we don't know, we have to try the move (we can't say that it's bad)
    return False


def quiescence(
    b: Board,
    depth: int,
    pv: deque[Move],
    eval_fn: Eval_fn,
    alpha: int,
    beta: int,
    transposition_table: TranspositionTable | None = None,
    move_ordering_fn: Move_ordering_fn = no_ordering,
) -> Node:
    stand_pat: int = eval_fn(b, transposition_table)

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
        b,
        depth,
        pv,
        eval_fn,
        -VALUE_MAX,
        VALUE_MAX,
        transposition_table,
        move_ordering_fn,
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
) -> Node:

    assert depth >= 0, depth

    # test null move in quiescence search
    if (
        b.moves_history[-1].is_null
    ):
        value = eval_fn(b, transposition_table)
        return Node(
            value=value,
            depth=depth,
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
        value = eval_fn(b, transposition_table)
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

    moves: Iterable[Move] = [x for x in board.pseudo_legal_moves(b, True) if not is_bad_capture(b, x)]
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
        node = _search(
            nb,
            depth - 1,
            curr_pv,
            eval_fn,
            alpha,
            beta,
            transposition_table,
            move_ordering_fn,
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
            value=eval_fn(b, transposition_table),
            pv=pv,
            full_move=b.full_move,
            lower=alpha,
            upper=beta,
            children=children,
        )

    return node
