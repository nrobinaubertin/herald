import multiprocessing
import time
from typing import Any, Optional

from . import board
from . import utils
from .board import Board
from .configuration import Config
from .constants import COLOR_DIRECTION, VALUE_MAX
from .search import Search, search


# wrapper around the search function to allow for multiprocess time management
def search_wrapper(
    queue: Any,
    b: Board,
    depth: int,
    config: Config,
    last_search: Search,
    children: int,
    transposition_table: dict,
    hash_move_tt: dict,
) -> None:
    search(
        b=b,
        depth=depth,
        config=config,
        last_search=last_search,
        children=children,
        transposition_table=transposition_table,
        hash_move_tt=hash_move_tt,
        queue=queue,
    )
    queue.close()


def itdep(
    queue: Any,
    b: Board,
    config: Config,
    movetime: int = 0,
    max_depth: int = 10,
    print_uci: bool = True,
    last_search: Search | None = None,
) -> Optional[Search]:
    # clear transposition table at each new search
    # there seems to be collision/memory issues that I don't have time to handle now
    config.transposition_table.clear()
    config.hash_move_tt.clear()

    if last_search is not None and config.use_saved_search:
        # try to find a useful subsearch in the last_search
        for move in last_search.pv:
            if hash(last_search.board) == hash(b) or len(last_search.pv) < 2:
                break
            # compute next subsearch
            last_search = Search(
                board=board.push(
                    last_search.board,
                    move,
                ),
                move=last_search.pv[1],
                pv=last_search.pv[1:],
                depth=last_search.depth - 1,
                nodes=0,
                score=last_search.score,
                time=0,
            )
        # clear last_search if it can't be used
        if hash(last_search.board) != hash(b):
            last_search = None
        else:
            last_search.end = False
            last_search.stop_search = False

    if last_search is not None and config.use_saved_search:
        start_depth = len(last_search.pv) + 1
    else:
        start_depth = 1

    if movetime > 0:
        start_time = time.time_ns()
        max_depth = max(
            1,
            min(
                10,
                max_depth,
            ),
        )
        for i in range(
            start_depth,
            max_depth + 1,
        ):
            # we create a queue to be able to stop the search when there's no time left
            # pylint issue: https://github.com/PyCQA/pylint/issues/3488
            # pylint: disable=unsubscriptable-object
            subqueue: multiprocessing.Queue[
                tuple[
                    Search,
                    Config,
                ]
                | None
            ] = multiprocessing.Queue()
            process = multiprocessing.Process(
                target=search_wrapper,
                args=(
                    subqueue,
                    b,
                ),
                kwargs={
                    "depth": i,
                    "config": config,
                    "last_search": last_search,
                    "children": 0 if last_search is None else last_search.nodes,
                    "transposition_table": config.transposition_table,
                    "hash_move_tt": config.hash_move_tt,
                },
                daemon=False,
            )
            process.start()

            current_search: Search | None = None
            while True:
                # we sometime check if we got a move out of the queue
                try:
                    ret: tuple[
                        Search,
                        Config,
                    ] | None = subqueue.get(
                        True,
                        0.1,
                    )

                    if ret is not None:
                        (
                            current_search,
                            config,
                        ) = ret

                    # if there is no move available and no exception was raised
                    if current_search is None:
                        # This is not strictly UCI but helps for evaluation/versus.py
                        if print_uci:
                            print("bestmove nomove")
                        return None

                except Exception:
                    current_search = None

                if current_search is not None:
                    last_search = current_search

                # bail out if the search tells us to stop
                assert isinstance(
                    last_search,
                    Search,
                )
                if last_search is not None and last_search.stop_search:
                    if __debug__:
                        print("stop_search")
                    process.terminate()
                    subqueue.close()
                    queue.put(last_search)
                    if print_uci:
                        print(f"bestmove {utils.to_uci(last_search.move)}")
                    return last_search

                # bail out if we have a mate
                if (
                    last_search is not None
                    and COLOR_DIRECTION[b.turn] * last_search.score >= VALUE_MAX
                ):
                    if __debug__:
                        print("mate")
                    queue.put(last_search)
                    if print_uci:
                        print(f"bestmove {utils.to_uci(last_search.move)}")
                    return last_search

                # calculate used time
                used_time = int(
                    max(
                        1,
                        (time.time_ns() - start_time) // 1e8,
                    )
                )

                # bail out if we have no time anymore
                if used_time + 1 >= movetime:
                    if __debug__:
                        print("no_time")
                    process.terminate()
                    subqueue.close()
                    queue.put_nowait(last_search)
                    if last_search is not None and print_uci:
                        print(f"bestmove {utils.to_uci(last_search.move)}")
                        return last_search
                    return None

                if last_search is not None and last_search.end and last_search.depth >= i:
                    if __debug__:
                        print(f"end_search: {last_search.depth}")
                    process.terminate()
                    subqueue.close()
                    break

        queue.put(last_search)
        if last_search is not None and print_uci:
            print(f"bestmove {utils.to_uci(last_search.move)}")
            return last_search

        return None

    last_search = None
    for i in range(
        start_depth,
        max_depth + 1,
    ):
        children = 0
        if last_search is not None:
            children = last_search.nodes
        ret = search(b=b, depth=i, last_search=last_search, config=config, children=children)

        if ret is not None:
            (
                current_search,
                config,
            ) = ret

        # if there is no move available
        if current_search is None:
            # This is not strictly UCI but helps for evaluation/versus.py
            if print_uci:
                print("bestmove nomove")
            return None

        last_search = current_search
        if current_search.stop_search:
            break

    if last_search is not None and print_uci:
        print(f"bestmove {utils.to_uci(last_search.move)}")
    if queue is not None:
        queue.put(last_search)
    return last_search
