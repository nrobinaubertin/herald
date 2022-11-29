from collections import deque
import time
from .constants import COLOR, VALUE_MAX
from . import board
from .algorithms import Alg_fn
from .evaluation import eval_simple, PIECE_VALUE
from .data_structures import Node, Search, Board
from .transposition_table import TranspositionTable
from . import move_ordering


def search(
    b: Board,
    depth: int,
    alg_fn: Alg_fn,
    transposition_table: TranspositionTable | None = None,
    last_search: Search | None = None,
) -> Search | None:

    start_time = time.time_ns()

    best = Node(
        depth=depth,
        value=(VALUE_MAX if b.turn == COLOR.BLACK else -VALUE_MAX),
    )

    possible_moves = [x for x in board.legal_moves(b)]

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

    alpha: int = -VALUE_MAX
    beta: int = VALUE_MAX
    children: int = 1

    possible_moves = sorted(
        possible_moves,
        key=lambda x: (
            int(x.is_capture)
            * (
                1000
                + PIECE_VALUE[abs(b.squares[x.end])] * 1000
                - PIECE_VALUE[abs(b.squares[x.start])]
            ) * b.turn
        ),
        reverse=b.turn == COLOR.WHITE
    )

    # move move_guess to the first place
    if isinstance(last_search, Search):
        for i, m in enumerate(possible_moves):
            if (
                m.start == last_search.move.start
                and m.end == last_search.move.end
            ):
                possible_moves = [possible_moves[i]] + \
                    possible_moves[:i] + possible_moves[i:]
                break

    for move in possible_moves:

        # return immediatly if this is a king capture
        if move.is_king_capture:
            return Search(
                move=move,
                pv=deque([move]),
                depth=1,
                nodes=children,
                score=VALUE_MAX * b.turn,
                time=(time.time_ns() - start_time),
                best_node=best,
            )

        node = alg_fn(
            board.push(b, move),
            depth,
            deque([move]),
            eval_simple,
            alpha,
            beta,
            transposition_table,
            move_ordering.mvv_lva,
        )

        children += node.children

        if b.turn == COLOR.WHITE:
            if node.value >= best.value:
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
            if node.value <= best.value:
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

    if best is None:
        return None

    return Search(
        move=best.pv[0],
        pv=best.pv,
        depth=depth,
        nodes=children,
        score=best.value,
        time=(time.time_ns() - start_time),
        best_node=best,
    )
