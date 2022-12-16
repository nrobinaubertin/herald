from collections import deque
import time
from .constants import COLOR, VALUE_MAX
from . import board
from .algorithms import Alg_fn
from .evaluation import eval_simple
from .data_structures import Node, Search, Board, MoveType
from .transposition_table import TranspositionTable
from . import move_ordering


def search(
    b: Board,
    depth: int,
    alg_fn: Alg_fn,
    transposition_table: TranspositionTable | None = None,
    qs_tt: TranspositionTable | None = None,
    last_search: Search | None = None,
) -> Search | None:

    start_time = time.time_ns()

    best = Node(
        depth=depth,
        value=(VALUE_MAX if b.turn == COLOR.BLACK else -VALUE_MAX),
    )

    possible_moves = [x for x in board.legal_moves(b)]

    # return None if there is no possible move
    if len(possible_moves) == 0:
        return None

    # if there's only one move possible, return it immediately
    if len(possible_moves) == 1:
        return Search(
            move=possible_moves[0],
            pv=[possible_moves[0]],
            depth=0,
            nodes=1,
            score=0,
            time=(time.time_ns() - start_time),
            best_node=Node(depth=0, value=0),
            stop_search=True,
        )

    # return immediatly if there is a king capture
    for move in possible_moves:
        if move.is_king_capture:
            return Search(
                move=move,
                pv=deque([move]),
                depth=1,
                nodes=1,
                score=VALUE_MAX * b.turn,
                time=(time.time_ns() - start_time),
                best_node=best,
            )

    alpha: int = -VALUE_MAX
    beta: int = VALUE_MAX

    # # Assume that we are not in zugzwang and that we can find a move that improves the situation
    # if b.turn == COLOR.WHITE:
    #     alpha = eval_simple(b)
    # else:
    #     beta = eval_simple(b)

    children: int = 1

    options = {
        "quiescence_search": True,
        "quiescence_depth": 13,
    }

    # # we seem to evaluate less node w/ this roughness value
    # ROUGHNESS: int = 1000

    # while alpha < beta - ROUGHNESS:
    #     current_value = (alpha + beta + 1) // 2
    #     node = alg_fn(
    #         b,
    #         depth,
    #         deque([]),
    #         eval_simple,
    #         current_value,
    #         current_value + 1,
    #         transposition_table,
    #         move_ordering.mvv_lva,
    #         MoveType.LEGAL,
    #         options,
    #     )
    #     children += node.children
    #     if node.value > current_value:
    #         alpha = node.value
    #     else:
    #         beta = node.value

    # node = alg_fn(
    #     b,
    #     depth,
    #     deque([]),
    #     eval_simple,
    #     alpha - ROUGHNESS//2,
    #     beta + ROUGHNESS//2,
    #     transposition_table,
    #     move_ordering.mvv_lva,
    #     MoveType.LEGAL,
    #     options,
    # )

    node = alg_fn(
        b,
        depth,
        deque([]),
        eval_simple,
        alpha,
        beta,
        transposition_table,
        qs_tt,
        move_ordering.mvv_lva,
        MoveType.LEGAL,
        options,
    )

    return Search(
        move=node.pv[0],
        pv=node.pv,
        depth=node.depth,
        nodes=node.children,
        score=node.value,
        time=(time.time_ns() - start_time),
        best_node=node,
    )
