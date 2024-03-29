"""Recursive search algorithms."""

from typing import Callable, Iterable, Optional

from . import board, evaluation
from .board import Board
from .configuration import Config
from .constants import COLOR, COLOR_DIRECTION, VALUE_MAX
from .data_structures import Move, Node

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


# alphabeta pruning (fail-soft)
# with optional move ordering and transposition table
def alphabeta(  # noqa: C901
    *,
    config: Config,
    b: Board,
    depth: int,
    pv: list[Move],
    gen_legal_moves: bool = False,
    alpha: int = -VALUE_MAX,
    beta: int = VALUE_MAX,
    max_depth: int = 0,
    children: int = 0,
    killer_moves: set[Move] | None = None,
) -> Iterable[Node]:
    # detect repetitions
    if depth != max_depth and b in b.hash_history:
        yield Node(
            depth=depth,
            value=0,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=children,
        )
        return

    if config.use_transposition_table and len(pv) > 0:
        # check if we find a hit in the transposition table
        node = config.transposition_table.get(
            b,
            depth,
        )
        if (
            isinstance(
                node,
                Node,
            )
            and node.depth >= depth
        ):
            # first we make sure that the retrieved node
            # is in our alpha-beta range
            if alpha < node.lower and node.upper < beta:
                # if this is a cut-node
                if node.value >= node.upper:
                    alpha = max(
                        alpha,
                        node.value,
                    )

                # if this is an all-node
                if node.value <= node.lower:
                    beta = min(
                        beta,
                        node.value,
                    )

                # if this is an exact node
                if node.lower < node.value < node.upper:
                    yield node
                    return

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
            value = evaluation.eval_fast(
                b.squares,
                b.remaining_material,
            )

        yield Node(
            value=value,
            depth=0,
            pv=pv,
            lower=alpha,
            upper=beta,
            children=children,
        )
        return

    best = None
    best_move = None

    moves: Iterable[Move] = []
    if gen_legal_moves:
        moves = board.legal_moves(b)
    else:
        moves = board.pseudo_legal_moves(b)

    moves = config.move_ordering_fn(
        b,
        moves,
    )

    def order_moves() -> Iterable[Move]:
        yielded = set()
        hash_move: Optional[Move] = config.hash_move_tt.get(
            b,
            None,
        )
        if hash_move is not None:
            yielded.add(hash_move)
            yield hash_move
        killer_moves_yielded = False
        for move in moves:
            if move in yielded:
                continue
            if move.is_capture and move.captured_piece > 2:
                yielded.add(move)
                yield move
                continue
            if config.use_killer_moves and killer_moves is not None and not killer_moves_yielded:
                for km in config.move_ordering_fn(
                    b,
                    (
                        km
                        for km in killer_moves
                        if board.is_pseudo_legal_move(
                            b,
                            km,
                        )
                    ),
                ):
                    if km not in yielded:
                        yielded.add(km)
                        yield km
                killer_moves_yielded = True
            if move in yielded:
                continue
            yielded.add(move)
            yield move

    # create the list of the killer moves that will be found in the children nodes
    next_killer_moves: set[Move] = set()

    moves_searched: int = 0

    for move in order_moves():
        moves_searched += 1

        curr_pv = pv.copy()
        curr_pv.append(move)

        # return immediately if this is a king capture
        if move.is_king_capture:
            yield Node(
                value=VALUE_MAX * b.turn,
                depth=depth,
                pv=curr_pv,
                lower=alpha,
                upper=beta,
                children=children,
            )
            return

        nb = board.push(
            b,
            move,
        )

        # if the king is in check after we move
        # then it's a bad move (we will lose the game)
        if board.king_is_in_check(
            nb,
            nb.invturn,
        ):
            continue

        new_depth = depth - 1

        # Late move reduction (LMR)
        if config.use_late_move_reduction and not move.is_capture:
            if moves_searched > 3 + depth * 3:
                new_depth = depth - 1
            if moves_searched > 4 + depth * 6:
                new_depth = depth - 2
            if moves_searched > 4 + depth * 8:
                new_depth = depth - 3

        for node in alphabeta(
            config=config,
            b=nb,
            depth=new_depth,
            pv=curr_pv,
            gen_legal_moves=False,
            alpha=alpha,
            beta=beta,
            max_depth=max_depth,
            children=children,
            killer_moves=next_killer_moves,
        ):
            continue

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
            alpha = max(
                alpha,
                node.value,
            )
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
            beta = min(
                beta,
                node.value,
            )
            if node.value <= alpha:
                if config.use_killer_moves and killer_moves is not None:
                    killer_moves.add(move)
                break

        # print our intermediary result
        if max_depth != 0 and best is not None and depth == max_depth and has_changed:
            yield best

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
        if board.is_square_attacked(
            b.squares,
            b.king_squares[b.turn],
            b.invturn,
        ):
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

    yield node
