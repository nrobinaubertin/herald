import time
import multiprocessing
from engine.board import Board
from engine.search import search
from engine.data_structures import to_uci


# This function should evaluate if we have time to think deeper
def is_there_time(
    used_time: int,
    current_depth: int,
    remaining_time: int,
    inc_time: int,
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
def search_wrapper(queue, board: Board, depth: int, rand_count: int, transposition_table):
    best = search(
        board,
        depth=depth,
        rand_count=rand_count,
        transposition_table=transposition_table,
    )
    queue.put_nowait(best)
    queue.close()


def best_move(
    board: Board,
    max_time: int = 0,
    inc_time: int = 0,
    max_depth: int = 0,
    eval_guess: int = 0,
    rand_count: int = 1,
    transposition_table=None,
):
    if max_time != 0:
        start_time = time.time_ns()
        current_move = None

        for i in range((10 if max_depth == 0 else max_depth)):

            # we create a queue to be able to stop the search when there's no time left
            queue = multiprocessing.Queue()
            process = multiprocessing.Process(
                target=search_wrapper,
                args=(queue, board),
                kwargs={
                    "depth": i,
                    "rand_count": max(1, 2 * (5 - board.full_move)),
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
                    pass
                finally:
                    if current_search is not None:
                        current_move = current_search

                    # calculate used time
                    used_time = int(max(1, (time.time_ns() - start_time) // 1e9))

                    # bail out if we have something and no time anymore
                    if not is_there_time(
                        used_time, current_move.depth, max_time - used_time, inc_time
                    ):
                        process.terminate()
                        queue.close()
                        if current_move is not None:
                            print(f"bestmove {to_uci(current_move.move)}")
                        else:
                            # This is not strictly UCI but helps for evaluation/versus.py
                            print("bestmove nomove")
                        return

            if current_move is not None:
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

                used_time = int(max(1, (time.time_ns() - start_time) // 1e9))
                if not is_there_time(
                    used_time, current_move.depth, max_time - used_time, inc_time
                ):
                    break
            else:
                break
    else:
        for i in range(max_depth + 1):
            current_move = search(
                board,
                depth=i,
                transposition_table=transposition_table,
            )
            if current_move is not None:
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

    if current_move is not None:
        print(f"bestmove {to_uci(current_move.move)}")
    else:
        # This is not strictly UCI but helps for evaluation/versus.py
        print("bestmove nomove")
