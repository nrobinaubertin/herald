import time
import multiprocessing
from engine.search import search
from engine.data_structures import to_uci, Search, Board
from engine.transposition_table import TranspositionTable


# This function should evaluate if we have time to think deeper
def is_there_time(
    used_time: int,
    remaining_time: int,
) -> bool:

    # fail-safe if there's no time left
    if remaining_time < 2:
        print("info no time left")
        return False

    if remaining_time < used_time:
        print("info no time for next depth")
        return False

    return True


# wrapper around the search function to allow for multiprocess time management
def search_wrapper(
    queue,
    b: Board,
    depth: int,
    rand_count: int,
    transposition_table: TranspositionTable | None = None,
    eval_guess: int = 0,
) -> None:
    best = search(
        b,
        depth=depth,
        rand_count=rand_count,
        transposition_table=transposition_table,
        eval_guess=eval_guess
    )
    queue.put_nowait(best)
    queue.close()


def best_move(
    b: Board,
    max_time: int = 0,
    inc_time: int = 0,
    max_depth: int = 0,
    eval_guess: int = 0,
    rand_count: int = 1,
    transposition_table: TranspositionTable | None = None,
) -> None:

    current_move = None

    if max_time != 0:
        start_time = time.time_ns()

        last_search: Search | None = None
        for i in range((10 if max_depth == 0 else max_depth)):

            # we create a queue to be able to stop the search when there's no time left
            queue: multiprocessing.Queue[Search | None] = multiprocessing.Queue()
            process = multiprocessing.Process(
                target=search_wrapper,
                args=(queue, b),
                kwargs={
                    "depth": i,
                    "rand_count": max(1, 2 * (5 - b.full_move)),
                    "transposition_table": transposition_table,
                },
                daemon=False,
            )
            process.start()

            current_search: Search | None = None
            while current_search is None:

                # every second, we check if we got a move out of the queue
                try:
                    current_search = queue.get(True, 1)

                    # if there is no move available
                    if current_search is None:
                        # This is not strictly UCI but helps for evaluation/versus.py
                        print("bestmove nomove")
                        return

                except:
                    current_search = None

                # calculate used time
                used_time = int(max(1, (time.time_ns() - start_time) // 1e9))

                if isinstance(current_search, Search) and current_search is not None:

                    last_search = current_search

                    print(
                        ""
                        + f"info depth {current_search.depth} "
                        + f"score cp {current_search.score} "
                        + f"time {int(current_search.time // 1e9)} "
                        + f"nodes {current_search.nodes} "
                        + (
                            "nps "
                            + str(
                                int(
                                    current_search.nodes
                                    * 1e9
                                    // max(0.001, current_search.time)
                                )
                            )
                            + " " if current_search.time > 0 else ""
                        )
                        + f"pv {' '.join([to_uci(x) for x in current_search.pv])}"
                    )

                    if current_search.stop_search:
                        process.terminate()
                        queue.close()
                        print(f"bestmove {to_uci(current_search.move)}")
                        return

                # bail out if we have something and no time anymore
                if not is_there_time(used_time, max_time - used_time):
                    process.terminate()
                    queue.close()
                    if last_search is not None:
                        print(f"bestmove {to_uci(last_search.move)}")
                    return
    else:
        last_search = None
        for i in range(max_depth + 1):
            current_search = search(
                b,
                depth=i,
                transposition_table=transposition_table,
            )

            # if there is no move available
            if current_search is None:
                # This is not strictly UCI but helps for evaluation/versus.py
                print("bestmove nomove")
                return

            print(
                ""
                + f"info depth {current_search.depth} "
                + f"score cp {current_search.score} "
                + f"time {int(current_search.time // 1e9)} "
                + f"nodes {current_search.nodes} "
                + (
                    "nps "
                    + str(
                        int(
                            current_search.nodes
                            * 1e9
                            // max(0.0001, current_search.time)
                        )
                    )
                    + " " if current_search.time > 0 else ""
                )
                + f"pv {' '.join([to_uci(x) for x in current_search.pv])}"
            )

            last_search = current_search
            if current_search.stop_search:
                break

        if last_search is not None:
            print(f"bestmove {to_uci(last_search.move)}")
