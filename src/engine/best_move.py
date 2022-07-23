import sys
import time
import multiprocessing
from engine.constants import COLOR
from engine.board import Board
from engine.search import search
from engine.transposition_table import TranspositionTable
from engine.evaluation import eval_board
from engine.data_structures import to_uci


# This function should evaluate if we have time to think deeper
def is_there_time(
    used_time: int,
    current_depth: int,
    remaining_time: int,
    inc_time: int,
    turn: int
) -> bool:

    # fail-safe if there's no time left
    if remaining_time < 2:
        print(f"info no time left")
        return False

    # try to estimate duration for the next depth
    next_depth_duration = (current_depth + 1) * 5 + used_time * 5

    if remaining_time < next_depth_duration:
        print(f"info no time for next depth")
        return False

    # so, we have time to increase depth, but should we ?

    # maybe we have enough depth
    max_depth = min(8, (turn // 2) + 2)
    if current_depth >= max_depth:
        print(f"info depth is enough")
        return False

    # maybe we want to keep some time for the rest of the game
    remaining_turns = max(10, 40 - turn)
    time_budget = (remaining_time + remaining_turns * inc_time) // remaining_turns

    if time_budget < used_time:
        print(f"info no time budget left")
        return False

    return True


# wrapper around the search function to allow for multiprocess time management
def search_wrapper(queue, board, depth, rand_count, transposition_table):
    best = search(
        board,
        depth=depth,
        rand_count=rand_count,
        transposition_table=transposition_table,
    )
    queue.put_nowait(best)
    queue.close()



def best_move(
    board,
    max_time=0,
    inc_time=0,
    max_depth=0,
    eval_guess=0,
    rand_count=1,
    transposition_table=None,
):
    if max_time != 0:
        start_time = time.time_ns()
        best = None

        for i in range((10 if max_depth == 0 else max_depth)):
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

                try:
                    current_search = queue.get(True, 1)
                except:
                    pass
                finally:
                    if current_search is not None:
                        best = current_search

                    # calculate used time
                    used_time = max(1, (time.time_ns() - start_time) // 1e9)

                    # bail out if we have something and no time anymore
                    if not is_there_time(used_time, best.depth, max_time - used_time, inc_time, board.full_move) and best is not None:
                        process.terminate()
                        queue.close()
                        print(f"bestmove {to_uci(best.move)}")
                        return

            print(
                ""
                + f"info depth {best.depth} "
                + f"score cp {best.score} "
                + f"time {int(best.time // 1e9)} "
                + f"nodes {best.nodes} "
                + (
                    "nps " + str(int(best.nodes * 1e9 // max(0.001, best.time))) + " "
                    if best.time > 0
                    else ""
                )
                + f"pv {' '.join([to_uci(x) for x in best.pv])}"
            )

            used_time = max(1, (time.time_ns() - start_time) // 1e9)
            if not is_there_time(used_time, best.depth, max_time - used_time, inc_time, board.full_move):
                break
    else:
        for i in range(max_depth + 1):
            best = search(
                board,
                depth=i,
                transposition_table=transposition_table,
            )
            print(
                ""
                + f"info depth {best.depth} "
                + f"score cp {best.score} "
                + f"time {int(best.time // 1e9)} "
                + f"nodes {best.nodes} "
                + (
                    "nps " + str(int(best.nodes * 1e9 // max(0.0001, best.time))) + " "
                    if best.time > 0
                    else ""
                )
                + f"pv {' '.join([to_uci(x) for x in best.pv])}"
            )

    print(f"bestmove {to_uci(best.move)}")
