"""Recursive search algorithms."""

from typing import Callable, Iterable, Optional

from . import board, evaluation
from .board import Board
from .configuration import Config
from .constants import COLOR, COLOR_DIRECTION, VALUE_MAX
from .data_structures import Move, Node, to_uci

Alg_fn = Callable[
    [
        Config,
        Board,
        int,
        list[Move],
        bool,
        int | None,
        int | None,
    ],
    Node,
]


def to_string(node: Node) -> str:
    return (
        ""
        + f"info depth {node.depth} "
        + f"score cp {node.value} "
        + f"nodes {node.children} "
        + f"pv {' '.join([to_uci(x) for x in node.pv])}"
    )


# alphabeta pruning (fail-soft)
# with optional move ordering and transposition table
def alphabeta(
    config: Config,
    b: Board,
    depth: int,
    pv: list[Move],
    gen_legal_moves: bool = False,
    alpha: int = -VALUE_MAX,
    beta: int = VALUE_MAX,
    max_depth: int = 0,
    children: int = 0,
    killer_moves: set | None = None,
) -> Node:
    # detect repetitions
    if b.__hash__() in b.hash_history:
        return Node(
            depth=depth,
            value=0,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=children,
        )

    if config.use_transposition_table and len(pv) > 0:
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

    # if we are on a terminal node, return the evaluation
    if depth <= 0:
        value: int = 0
        if config.quiescence_search:
            node = config.quiescence_fn(
                config,
                b,
                pv,
                alpha,
                beta,
            )

            # type ignore because mypy doesn't see the qs fn
            children += node.children  # type: ignore
            value = node.value  # type: ignore
            if __debug__:
                # display quiescent nodes
                pv = node.pv  # type: ignore
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

    best = None
    best_move = None

    moves: Iterable[Move] = []
    if gen_legal_moves:
        moves = board.legal_moves(b)
    else:
        moves = board.pseudo_legal_moves(b)

    moves = config.move_ordering_fn(b, moves)

    def order_moves() -> Iterable[Move]:
        yielded = set()
        hash_move: Optional[Move] = config.hash_move_tt.get(b, None)
        if hash_move is not None:
            yielded.add(hash_move)
            yield hash_move
        for move in moves:
            if move in yielded:
                continue
            if move.is_capture and move.captured_piece > 2:
                yielded.add(move)
                yield move
                continue
            if config.use_killer_moves and killer_moves is not None:
                for km in killer_moves:
                    if km not in yielded and board.is_pseudo_legal_move(b, km):
                        yielded.add(km)
                        yield km
            if move == hash_move:
                continue
            if config.use_killer_moves and killer_moves is not None:
                if move in killer_moves:
                    continue
            yielded.add(move)
            yield move

    # create the list of the killer moves that will be found in the children nodes
    next_killer_moves: set = set()

    for move in order_moves():
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

        nb = board.push(b, move)

        # if the king is in check after we move
        # then it's a bad move (we will lose the game)
        if board.king_is_in_check(nb, nb.invturn):
            continue

        node = alphabeta(
            config,
            nb,
            depth - 1,
            curr_pv,
            False,
            alpha,
            beta,
            max_depth,
            children,
            next_killer_moves,
        )

        children = node.children

        has_changed: bool = False
        if b.turn == COLOR.WHITE:
            if best is None or node.value > best.value:
                has_changed = True
                best_move = move
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                    lower=alpha,
                    upper=beta,
                    children=children,
                )
            alpha = max(alpha, node.value)
            if node.value >= beta:
                if config.use_killer_moves and killer_moves is not None:
                    killer_moves.add(move)
                break
        else:
            if best is None or node.value < best.value:
                has_changed = True
                best_move = move
                best = Node(
                    value=node.value,
                    depth=depth,
                    pv=node.pv,
                    lower=alpha,
                    upper=beta,
                    children=children,
                )
            beta = min(beta, node.value)
            if node.value <= alpha:
                if config.use_killer_moves and killer_moves is not None:
                    killer_moves.add(move)
                break

        # print our intermediary result
        if max_depth != 0 and best is not None and depth == max_depth and has_changed:
            print(to_string(best))

    if config.use_transposition_table:
        # Save the resulting best node in the transposition table
        if best is not None and best.depth > 0:
            config.transposition_table[b] = best
        if config.use_hash_move:
            if best_move is not None:
                config.hash_move_tt[b] = best_move

    if best is not None:
        node = Node(
            depth=best.depth,
            value=best.value,
            pv=best.pv,
            lower=alpha,
            upper=beta,
            children=children,
        )
    else:
        # no "best" found
        # should happen only in case of stalemate/checkmate
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
            node = Node(
                depth=depth,
                value=0,
                pv=pv,
                lower=alpha,
                upper=beta,
                children=children,
            )

    return node


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
            value=evaluation.eval_fast(b.squares, b.remaining_material),
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
    for move in config.move_ordering_fn(b, moves):
        curr_board = board.push(b, move)
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
        if board.king_is_in_check(curr_board, curr_board.invturn):
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

    if isinstance(best, Node):
        return Node(
            value=best.value,
            depth=best.depth,
            pv=best.pv,
            children=children,
        )

    # no "best" found
    # should happen only in case of stalemate/checkmate
    if board.is_square_attacked(b.squares, b.king_squares[b.turn], b.invturn):
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
