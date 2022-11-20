from collections import deque
import time
import random
from .constants import COLOR, VALUE_MAX
from . import board
from .algorithms import Alg_fn
from .evaluation import eval_simple, PIECE_VALUE
from .data_structures import Node, Search, Board, Move
from .transposition_table import TranspositionTable
from . import move_ordering


def search(
    b: Board,
    depth: int,
    alg_fn: Alg_fn,
    rand_count: int = 1,
    transposition_table: TranspositionTable | None = None,
    eval_guess: int = 0,
    move_guess: Move | None = None,
) -> Search | None:

    start_time = time.time_ns()

    best = Node(
        depth=depth,
        value=(VALUE_MAX if b.turn == COLOR.BLACK else -VALUE_MAX),
    )
    node_count = 0
    nodes = []

    possible_moves = board.legal_moves(b)

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

    for move in possible_moves:
        curr_board = board.push(b, move)
        node = alg_fn(
            curr_board,
            depth,
            deque([move]),
            eval_simple,
            -VALUE_MAX,
            VALUE_MAX,
            transposition_table,
            move_ordering.mvv_lva,
        )
        node_count += node.children + 1
        nodes.append(Node(depth=depth, value=node.value, pv=node.pv))

    nodes = sorted(nodes, key=lambda x: x.value, reverse=b.turn == COLOR.WHITE)

    best = random.choice(nodes[:rand_count])

    if best is None:
        return None

    return Search(
        move=best.pv[0],
        pv=best.pv,
        depth=depth,
        nodes=node_count,
        score=best.value,
        time=(time.time_ns() - start_time),
        best_node=best,
    )


def better_search(
    b: Board,
    depth: int,
    alg_fn: Alg_fn,
    rand_count: int = 1,
    transposition_table: TranspositionTable | None = None,
    eval_guess: int = 0,
    move_guess: Move | None = None,
) -> Search | None:

    start_time = time.time_ns()

    best = Node(
        depth=depth,
        value=(VALUE_MAX if b.turn == COLOR.BLACK else -VALUE_MAX),
    )

    possible_moves = [x for x in board.legal_smart_moves(b)]

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
            int(x.move.is_capture)
            * (
                1000
                + PIECE_VALUE[abs(b.squares[x.move.end])] * 1000
                - PIECE_VALUE[abs(b.squares[x.move.start])]
            ) * b.turn
        ),
        reverse=b.turn == COLOR.WHITE
    )

    # move move_guess to the first place
    if isinstance(move_guess, Move):
        for i, sm in enumerate(possible_moves):
            if (
                sm.move.start == move_guess.start
                and sm.move.end == move_guess.end
            ):
                possible_moves = [possible_moves[i]] + possible_moves[:i] + possible_moves[i:]
                break

    for sm in possible_moves:

        # return immediatly if this is a king capture
        if sm.move.is_king_capture:
            return Search(
                move=sm.move,
                pv=deque([sm.move]),
                depth=1,
                nodes=children,
                score=VALUE_MAX * b.turn,
                time=(time.time_ns() - start_time),
                best_node=best,
            )

        node = alg_fn(
            sm.board,
            depth,
            deque([sm.move]),
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
