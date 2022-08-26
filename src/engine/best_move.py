import time
import multiprocessing
from engine.board import Board
from engine.search import search
from engine.data_structures import to_uci
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
def search_wrapper(queue, b: Board, depth: int, rand_count: int, transposition_table: TranspositionTable | None = None):
    best = search(
        b,
        depth=depth,
        rand_count=rand_count,
        transposition_table=transposition_table,
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
):

    current_move = None

    if max_time != 0:
        start_time = time.time_ns()

        for i in range((10 if max_depth == 0 else max_depth)):

            # we create a queue to be able to stop the search when there's no time left
            queue = multiprocessing.Queue()
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

            current_search = None
            while current_search is None:

                # every second, we check if we got a move out of the queue
                try:
                    current_search = queue.get(True, 1)
                except:
                    current_search = "Searching"

                # if there is no move available
                if current_search is None:
                    # This is not strictly UCI but helps for evaluation/versus.py
                    print("bestmove nomove")
                    return

                if current_search != "Searching":
                    current_move = current_search
                    print(
                        ""
                        + f"info depth {current_move.depth} "
                        + f"score cp {current_move.score} "
                        + f"time {int(current_move.time // 1e9)} "
                        + f"nodes {current_move.nodes} "
                        + (
                            "nps "
                            + str(
                                int(
                                    current_move.nodes
                                    * 1e9
                                    // max(0.001, current_move.time)
                                )
                            )
                            + " "
                            if current_move.time > 0
                            else ""
                        )
                        + f"pv {' '.join([to_uci(x) for x in current_move.pv])}"
                    )
                else:
                    current_search = None

                # calculate used time
                used_time = int(max(1, (time.time_ns() - start_time) // 1e9))

                # bail out if we have something and no time anymore
                if current_move.stop_search or not is_there_time(used_time, max_time - used_time):
                    process.terminate()
                    queue.close()
                    print(f"bestmove {to_uci(current_move.move)}")
                    return
    else:
        for i in range(max_depth + 1):
            current_move = search(
                b,
                depth=i,
                transposition_table=transposition_table,
            )

            # if there is no move available
            if current_move is None:
                # This is not strictly UCI but helps for evaluation/versus.py
                print("bestmove nomove")
                return

            print(
                ""
                + f"info depth {current_move.depth} "
                + f"score cp {current_move.score} "
                + f"time {int(current_move.time // 1e9)} "
                + f"nodes {current_move.nodes} "
                + (
                    "nps "
                    + str(
                        int(
                            current_move.nodes
                            * 1e9
                            // max(0.0001, current_move.time)
                        )
                    )
                    + " "
                    if current_move.time > 0
                    else ""
                )
                + f"pv {' '.join([to_uci(x) for x in current_move.pv])}"
            )

            if current_move.stop_search:
                break

        print(f"bestmove {to_uci(current_move.move)}")
