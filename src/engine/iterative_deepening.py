import time
import multiprocessing
from collections import deque
from .search import search
from .data_structures import to_uci, Search, Board, Move
from .constants import VALUE_MAX
from . import board
from .configuration import Config
import random


def to_string(search: Search) -> str:
    return (
        ""
        + f"info depth {search.depth} "
        + f"score cp {search.score} "
        + f"time {int(search.time // 1e9)} "
        + f"nodes {search.nodes} "
        + (
            "nps "
            + str(
                int(
                    search.nodes
                    * 1e9
                    // max(0.001, search.time)
                )
            )
            + " " if search.time > 0 else ""
        )
        + f"pv {' '.join([to_uci(x) for x in search.pv])}"
    )


# wrapper around the search function to allow for multiprocess time management
def search_wrapper(
    queue,
    b: Board,
    depth: int,
    config: Config,
    last_search: Search,
) -> None:
    best = search(
        b,
        depth=depth,
        config=config,
        last_search=last_search,
    )
    queue.put_nowait(best)
    queue.close()


def itdep(
    b: Board,
    config: Config,
    movetime: int = 0,
    max_depth: int = 10,
    print_uci: bool = True,
):
    # clear transposition tables at each new search
    # there seems to be collision issues that I don't have time to handle now
    config.transposition_table.clear()
    config.qs_transposition_table.clear()

    if movetime > 0:

        if board.to_fen(b) in config.opening_book:
            moves = config.opening_book[board.to_fen(b)]["moves"]
            move = random.choice(moves)["move"]
            move = Move(*[
                int(move[0]),
                int(move[1]),
                int(move[2]),
                bool(move[3]),
                bool(move[4]),
                int(move[5]),
                bool(move[6])
            ])
            if print_uci:
                print(f"bestmove {to_uci(move)}")
            return Search(
                move=move,
                pv=deque([move]),
                depth=0,
                nodes=1,
                score=0,
                time=1,
            )

        start_time = time.time_ns()
        last_search: Search | None = None
        max_depth = max(1, min(10, max_depth))
        for i in range(1, max_depth + 1):

            # we create a queue to be able to stop the search when there's no time left
            queue: multiprocessing.Queue[Search | None] = multiprocessing.Queue()
            process = multiprocessing.Process(
                target=search_wrapper,
                args=(queue, b),
                kwargs={
                    "depth": i,
                    "config": config,
                    "last_search": last_search,
                },
                daemon=False,
            )
            process.start()

            current_search: Search | None = None
            while current_search is None:

                # # every second, we check if we got a move out of the queue
                try:
                    current_search = queue.get(True, 1)

                    # if there is no move available and no exception was raised
                    if current_search is None:
                        # This is not strictly UCI but helps for evaluation/versus.py
                        if print_uci:
                            print("bestmove nomove")
                        return None

                except:
                    current_search = None

                if isinstance(current_search, Search):

                    last_search = current_search

                    if print_uci:
                        print(to_string(last_search))

                    # bail out if the search tells us to stop
                    if last_search.stop_search:
                        process.terminate()
                        queue.close()
                        if print_uci:
                            print(f"bestmove {to_uci(last_search.move)}")
                        return last_search

                # bail out if we have a mate
                if last_search is not None and abs(last_search.score) >= VALUE_MAX:
                    if print_uci:
                        print(f"bestmove {to_uci(last_search.move)}")
                    return last_search

                # calculate used time
                used_time = int(max(1, (time.time_ns() - start_time) // 1e9))

                # bail out if we have no time anymore
                if used_time + 1 >= movetime:
                    process.terminate()
                    queue.close()
                    if last_search is not None and print_uci:
                        print(f"bestmove {to_uci(last_search.move)}")
                        return last_search
                    return None

        if last_search is not None and print_uci:
            print(f"bestmove {to_uci(last_search.move)}")
            return last_search

        return None

    last_search = None
    for i in range(1, max_depth + 1):
        current_search = search(
            b,
            depth=i,
            last_search=last_search,
            config=config,
        )

        # if there is no move available
        if current_search is None:
            # This is not strictly UCI but helps for evaluation/versus.py
            if print_uci:
                print("bestmove nomove")
            return None

        if print_uci:
            print(to_string(current_search))

        last_search = current_search
        if current_search.stop_search:
            break

    if last_search is not None and print_uci:
        print(f"bestmove {to_uci(last_search.move)}")
    return last_search
