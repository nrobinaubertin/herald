"""Alphabeta search."""

from typing import Iterable, Optional
from . import board
from . import evaluation
from .board import Board
from .configuration import Config
from .constants import COLOR, COLOR_DIRECTION, VALUE_MAX
from .data_structures import Move, Node
from . import quiescence
from . import move_ordering


# alphabeta pruning (fail-soft)
# with optional move ordering and transposition table
def alphabeta(
    *,
    config: Config,
    b: Board,
    depth: int,
    pv: list[Move],
    gen_legal_moves: bool = False,
    alpha: int = -VALUE_MAX,
    beta: int = VALUE_MAX,
    max_depth: int = 0,
    killer_moves: set[Move] | None = None,
) -> int:
    # detect repetitions
    if depth != max_depth and b in b.hash_history:
        return 0

    if config.use_transposition_table:
        node = config.transposition_table.get(b, depth)
        if isinstance(node, Node) and node.depth >= depth:
            # first we make sure that the retrieved node
            # is in our alpha-beta range
            if alpha < node.lower and node.upper < beta:
                # if this is an exact node
                if node.lower < node.value < node.upper:
                    return node.value

    # if we are on a terminal node, return the evaluation
    if depth <= 0:
        if config.quiescence_search:
            value = quiescence.quiescence(config=config, b=b, alpha=alpha, beta=beta)
        else:
            value = evaluation.evaluation(b.squares, b.remaining_material)
        return value

    best: int | None = None
    best_move: Move | None = None
    child_pv: list[Move] = []

    moves: Iterable[Move] = []
    if gen_legal_moves:
        moves = board.legal_moves(b)
    else:
        moves = board.pseudo_legal_moves(b)

    moves = move_ordering.fast_ordering(b, moves)

    def order_moves() -> Iterable[Move]:
        yielded = set()
        hash_move: Optional[Move] = config.hash_move_tt.get(b, None)
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
                for km in move_ordering.fast_ordering(
                    b,
                    (km for km in killer_moves if board.is_pseudo_legal_move(b, km)),
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

        # return immediately if this is a king capture
        if move.is_king_capture:
            assert False, "KING CAPTURE: should not happen, code to remove"
            return VALUE_MAX * b.turn

        nb = board.push(b, move)

        # if the king is in check after we move
        # then it's a bad move (we will lose the game)
        if board.king_is_in_check(nb, nb.invturn):
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

        value = alphabeta(
            config=config,
            b=nb,
            depth=new_depth,
            pv=child_pv,
            gen_legal_moves=False,
            alpha=alpha,
            beta=beta,
            max_depth=max_depth,
            killer_moves=next_killer_moves,
        )

        # has_changed: bool = False
        if b.turn == COLOR.WHITE:
            if best is None or value > best:
                # has_changed = True
                best_move = move
                best = value
            if value > alpha:
                alpha = max(alpha, value)
                pv.clear()
                pv.append(move)
                pv += child_pv
            if value >= beta:
                if config.use_killer_moves and killer_moves is not None:
                    killer_moves.add(move)
                break
        else:
            if best is None or value < best:
                # has_changed = True
                best_move = move
                best = value
            if value < beta:
                beta = min(beta, value)
                pv.clear()
                pv.append(move)
                pv += child_pv
            if value <= alpha:
                if config.use_killer_moves and killer_moves is not None:
                    killer_moves.add(move)
                break

    if config.use_transposition_table:
        # Save the resulting best node in the transposition table
        if best is not None and depth > 0:
            node = Node(
                depth=depth,
                value=best,
                lower=alpha,
                upper=beta,
            )
            config.transposition_table[b] = node
        if config.use_hash_move:
            if best_move is not None:
                config.hash_move_tt[b] = best_move

    if best is not None and best_move is not None:
        return best
    else:
        # no "best" found
        # should happen only in case of stalemate/checkmate
        if board.is_square_attacked(
            b.squares,
            b.king_squares[b.turn],
            b.invturn,
        ):
            return VALUE_MAX * COLOR_DIRECTION[b.turn] * -1
        else:
            return 0
