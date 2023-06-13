"""Minimax algorithms."""

from typing import Iterable

from . import board, evaluation
from .board import Board
from .configuration import Config
from .constants import COLOR, VALUE_MAX
from .data_structures import Move, Node


# Simple minimax
def minimax(
    config: Config,
    b: Board,
    depth: int,
    pv: list[Move],
    gen_legal_moves: bool = False,
    alpha: int = 0,
    beta: int = 0,
) -> Node:
    assert depth >= 0, depth

    # if we are on a terminal node, return the evaluation
    if depth == 0:
        return Node(
            value=evaluation.eval_fast(
                b.squares,
                b.remaining_material,
            ),
            depth=0,
            pv=pv,
            children=1,
        )

    best = None

    # count the number of children (direct and non direct)
    # for info purposes
    children = 1

    moves: Iterable[Move] = []
    if gen_legal_moves:
        moves = board.legal_moves(b)
    else:
        moves = board.pseudo_legal_moves(b)
    for move in config.move_ordering_fn(
        b,
        moves,
    ):
        curr_board = board.push(
            b,
            move,
        )
        curr_pv = pv.copy()
        curr_pv.append(move)

        # return immediately if this is a king capture
        if move.is_king_capture:
            return Node(
                value=VALUE_MAX * b.turn,
                depth=depth,
                pv=curr_pv,
                children=children,
            )

        # if the king is in check after we move
        # then it's a bad move (we will lose the game)
        if board.king_is_in_check(
            curr_board,
            curr_board.invturn,
        ):
            continue

        node = minimax(
            config,
            curr_board,
            depth - 1,
            curr_pv,
            False,
        )

        children += node.children

        if b.turn == COLOR.WHITE:
            if best is None or node.value > best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                    children=children,
                )
        else:
            if best is None or node.value < best.value:
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                    children=children,
                )

    if isinstance(
        best,
        Node,
    ):
        return Node(
            value=best.value,
            depth=best.depth,
            pv=best.pv,
            children=children,
        )

    # no "best" found
    # should happen only in case of stalemate/checkmate
    if board.is_square_attacked(
        b.squares,
        b.king_squares[b.turn],
        b.invturn,
    ):
        return Node(
            depth=depth,
            value=VALUE_MAX * b.turn * -1,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=children,
        )
    return Node(
        depth=depth,
        value=0,
        pv=pv,
        lower=alpha,
        upper=beta,
        children=children,
    )
