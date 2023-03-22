import multiprocessing
import time
from dataclasses import dataclass
from typing import Optional

from . import algorithms, board
from .board import Board
from .configuration import Config
from .constants import COLOR_DIRECTION, VALUE_MAX
from .data_structures import Move


@dataclass
class Search:
    board: Board
    move: Move
    depth: int
    score: int
    nodes: int
    time: int
    pv: list[Move]
    stop_search: bool = False
    end: bool = False


def search(
    *,
    b: Board,
    depth: int,
    config: Config,
    last_search: Search | None = None,
    silent: bool = False,
    children: int = 0,
    transposition_table: dict | None = None,
    hash_move_tt: dict | None = None,
    queue: Optional[multiprocessing.Queue] = None,
) -> tuple[Search, Config] | None:
    if transposition_table is not None:
        config.transposition_table = transposition_table
    if hash_move_tt is not None:
        config.hash_move_tt = hash_move_tt

    start_time = time.time_ns()

    possible_moves = board.legal_moves(b)

    # return None if there is no possible move
    if len(possible_moves) == 0:
        if queue is None:
            return None
        else:
            queue.put(None)
            return None

    # if there's only one move possible, return it immediately
    if len(possible_moves) == 1:
        ret = (
            Search(
                board=b,
                move=possible_moves[0],
                pv=[possible_moves[0]],
                depth=0,
                nodes=1,
                score=0,
                time=(time.time_ns() - start_time),
                stop_search=True,
            ),
            config,
        )
        if queue is None:
            return ret
        else:
            queue.put(ret)
            return None

    # return immediately if there is a king capture
    for move in possible_moves:
        if move.is_king_capture:
            ret = (
                Search(
                    board=b,
                    move=move,
                    pv=[move],
                    depth=1,
                    nodes=1,
                    score=VALUE_MAX * b.turn,
                    time=(time.time_ns() - start_time),
                ),
                config,
            )
            if queue is None:
                return ret
            else:
                queue.put(ret)
                return None

    guess = last_search.score if last_search else 0
    MARGIN: int = 50
    lower = guess - MARGIN
    upper = guess + MARGIN
    iteration = 0

    while True:
        iteration += 1
        for node in algorithms.alphabeta(
            config=config,
            b=b,
            depth=depth,
            pv=[],
            gen_legal_moves=True,
            alpha=lower,
            beta=upper,
            max_depth=depth if not silent else 0,
            children=children,
            killer_moves=set(),
        ):
            children = node.children + 1
            search = Search(
                board=b,
                move=node.pv[0],
                pv=node.pv,
                depth=node.depth,
                nodes=children,
                score=node.value,
                time=(time.time_ns() - start_time),
                stop_search=(COLOR_DIRECTION[b.turn] * node.value) > VALUE_MAX - 100,
            )
            if queue is not None:
                queue.put((search, config))

        # if no best move was found
        # this could happen because of some pruning
        if not node.pv:
            upper += MARGIN * 2
            lower -= MARGIN * 2
            continue
        if node.value >= upper:
            upper += MARGIN * 2
            continue
        if node.value <= lower:
            lower -= MARGIN * 2
            continue
        break

    search.end = True
    return (search, config)
