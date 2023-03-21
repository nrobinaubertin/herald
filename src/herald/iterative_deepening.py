import multiprocessing
import time
from typing import Any, Optional

from . import board
from .board import Board
from .configuration import Config
from .constants import VALUE_MAX
from .data_structures import to_uci
from .search import Search, search


def to_string(search: Search) -> str:
    return (
        ""
        + f"info depth {search.depth} "
        + f"score cp {search.score} "
        + f"time {int(search.time // 1e9)} "
        + f"nodes {search.nodes} "
        + (
            "nps " + str(int(search.nodes * 1e9 // max(0.001, search.time))) + " "
            if search.time > 0
            else ""
        )
        + f"pv {to_uci(search.pv)}"
    )


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

    if last_search is not None:
        # try to find a useful subsearch in the last_search
        for move in last_search.pv:
            if hash(last_search.board) == hash(b):
                break
            # compute next subsearch
            last_search = Search(
                board=board.push(last_search.board, move),
                move=last_search.pv[1],
                pv=last_search.pv[1:],
                depth=last_search.depth - 1,
                nodes=0,
                score=last_search.score,
                time=0,
                stop_search=False,
            )
        # clear last_search if it can't be used
        if hash(last_search.board) != hash(b):
            last_search = None

    if last_search is not None:
        start_depth = len(last_search.pv) + 1
    else:
        start_depth = 1

    if movetime > 0:
        start_time = time.time_ns()
        max_depth = max(1, min(10, max_depth))
        for i in range(start_depth, max_depth + 1):
            # we create a queue to be able to stop the search when there's no time left
            # pylint issue: https://github.com/PyCQA/pylint/issues/3488
            # pylint: disable=unsubscriptable-object
            subqueue: multiprocessing.Queue[tuple[Search, Config] | None] = multiprocessing.Queue()
            process = multiprocessing.Process(
                target=search_wrapper,
                args=(subqueue, b),
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
            while current_search is None:
                # we sometime check if we got a move out of the queue
                try:
                    ret: tuple[Search, Config] | None = subqueue.get(True, 1)

                    if ret is not None:
                        (current_search, config) = ret

                    # if there is no move available and no exception was raised
                    if current_search is None:
                        # This is not strictly UCI but helps for evaluation/versus.py
                        if print_uci:
                            print("bestmove nomove")
                        return None

                except:
                    current_search = None

                if current_search is not None:
                    last_search = current_search

                # bail out if the search tells us to stop
                if last_search is not None and last_search.stop_search:
                    process.terminate()
                    subqueue.close()
                    queue.put_nowait(last_search)
                    if print_uci:
                        print(f"bestmove {to_uci(last_search.move)}")
                    return last_search

                # bail out if we have a mate
                if last_search is not None and abs(last_search.score) >= VALUE_MAX:
                    queue.put_nowait(last_search)
                    if print_uci:
                        print(f"bestmove {to_uci(last_search.move)}")
                    return last_search

                # calculate used time
                used_time = int(max(1, (time.time_ns() - start_time) // 1e8))

                # bail out if we have no time anymore
                if used_time + 1 >= movetime:
                    process.terminate()
                    subqueue.close()
                    queue.put_nowait(last_search)
                    if last_search is not None and print_uci:
                        print(f"bestmove {to_uci(last_search.move)}")
                        return last_search
                    return None

        queue.put_nowait(last_search)
        if last_search is not None and print_uci:
            print(f"bestmove {to_uci(last_search.move)}")
            return last_search

        return None

    last_search = None
    for i in range(start_depth, max_depth + 1):
        ret = search(
            b=b,
            depth=i,
            last_search=last_search,
            config=config,
            children=0 if last_search is None else last_search.nodes,
        )

        if ret is not None:
            current_search, config = ret

        # if there is no move available
        if current_search is None:
            # This is not strictly UCI but helps for evaluation/versus.py
            if print_uci:
                print("bestmove nomove")
            return None

        # if print_uci:
        #     print(to_string(current_search))

        last_search = current_search
        if current_search.stop_search:
            break

    if last_search is not None and print_uci:
        print(f"bestmove {to_uci(last_search.move)}")
    queue.put_nowait(last_search)
    return last_search
