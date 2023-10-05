import multiprocessing
import time
from dataclasses import dataclass
from typing import Optional

from . import alphabeta, board
from . import utils
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
    time: int
    pv: list[Move]
    stop_search: bool = False
    end: bool = False

    def __str__(
        self,
    ) -> str:
        return (
            ""
            + f"info depth {self.depth} "
            + f"score cp {self.score} "
            + f"time {int(self.time // 1e9)} "
            + f"pv {utils.to_uci(self.pv)}"
        )


def search(
    *,
    b: Board,
    depth: int,
    config: Config,
    last_search: Search | None = None,
    silent: bool = False,
    transposition_table: dict | None = None,
    hash_move_tt: dict | None = None,
    queue: Optional[multiprocessing.Queue] = None,
) -> Search | None:
    start_time = time.time_ns()

    def handle_search(search: Search | None):
        if search is not None:
            print(search)
        if queue is not None:
            queue.put(search)
        return search

    if transposition_table is not None:
        config.transposition_table = transposition_table
    if hash_move_tt is not None:
        config.hash_move_tt = hash_move_tt

    possible_moves = board.legal_moves(b)

    # return None if there is no possible move
    if len(possible_moves) == 0:
        return handle_search(None)

    # if there's only one move possible, return it immediately
    if len(possible_moves) == 1:
        ret = Search(
            board=b,
            move=possible_moves[0],
            pv=[possible_moves[0]],
            depth=0,
            score=0,
            time=(time.time_ns() - start_time),
            stop_search=True,
        )
        return handle_search(ret)

    # return immediately if there is a king capture
    for move in possible_moves:
        if move.is_king_capture:
            ret = Search(
                board=b,
                move=move,
                pv=[move],
                depth=1,
                score=VALUE_MAX * b.turn,
                time=(time.time_ns() - start_time),
            )
            return handle_search(ret)

    guess = last_search.score if last_search else 0
    margin: int = 50
    lower = guess - margin
    upper = guess + margin
    iteration = 0

    while True:
        iteration += 1
        pv: list[Move] = []
        value = alphabeta.alphabeta(
            config=config,
            b=b,
            depth=depth,
            pv=pv,
            gen_legal_moves=True,
            alpha=lower,
            beta=upper,
            killer_moves=set(),
        )

        # if no best move was found
        # this could happen because of some pruning
        if not pv:
            upper += margin * 2
            lower -= margin * 2
            continue
        if value >= upper:
            upper += margin * 2
            continue
        if value <= lower:
            lower -= margin * 2
            continue
        break

    search = Search(
        board=b,
        move=pv[0],
        pv=pv,
        depth=depth,
        score=value,
        time=(time.time_ns() - start_time),
        stop_search=(COLOR_DIRECTION[b.turn] * value) > VALUE_MAX - 100,
    )
    search.end = True
    return handle_search(search)
