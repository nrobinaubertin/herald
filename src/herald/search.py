import time
from collections import deque, namedtuple

from . import board
from .board import Board
from .configuration import Config
from .constants import VALUE_MAX

Search = namedtuple(
    "Search",
    [
        "move",
        "depth",
        "score",
        "nodes",
        "time",
        "pv",
        "stop_search",
    ],
    defaults=[False],
)


def search(
    b: Board,
    depth: int,
    config: Config,
    last_search: Search | None = None,
) -> Search | None:
    start_time = time.time_ns()

    config.set_depth(depth)

    possible_moves = board.legal_moves(b)

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
            stop_search=True,
        )

    # return immediately if there is a king capture
    for move in possible_moves:
        if move.is_king_capture:
            return Search(
                move=move,
                pv=deque([move]),
                depth=1,
                nodes=1,
                score=VALUE_MAX * b.turn,
                time=(time.time_ns() - start_time),
            )

    guess = last_search.score if last_search else 0
    lower = guess - 50
    upper = guess + 50
    iteration = 0

    # count the number of children (direct and non direct)
    # for info purposes
    children: int = 1

    while True:
        iteration += 1
        node = config.alg_fn(
            config,
            b,
            depth,
            deque([]),
            True,
            lower,
            upper,
        )
        children += node.children + 1
        # if no best move was found
        # this could happen because of some pruning
        if not node.pv:
            upper += 50 * (iteration**2)
            lower -= 50 * (iteration**2)
            continue
        if node.value >= upper:
            upper += 50 * (iteration**2)
            continue
        if node.value <= lower:
            lower -= 50 * (iteration**2)
            continue
        break

    return Search(
        move=node.pv[0],
        pv=node.pv,
        depth=node.depth,
        nodes=children,
        score=node.value,
        time=(time.time_ns() - start_time),
        stop_search=abs(node.value) > VALUE_MAX - 100,
    )
