import time
import multiprocessing
from collections import deque
from .search import search
from .data_structures import to_uci, Search, Board, Move
from .algorithms import Alg_fn
from .transposition_table import TranspositionTable
from .constants import VALUE_MAX
from . import board


# wrapper around the search function to allow for multiprocess time management
def search_wrapper(
    queue,
    b: Board,
    depth: int,
    alg_fn: Alg_fn,
    transposition_table: TranspositionTable | None = None,
    qs_tt: TranspositionTable | None = None,

) -> None:
    best = search(
        b,
        depth=depth,
        transposition_table=transposition_table,
        qs_tt=transposition_table,
        alg_fn=alg_fn,
    )
    queue.put_nowait(best)
    queue.close()


def itdep(
    b: Board,
    alg_fn: Alg_fn,
    movetime: int = 0,
    max_depth: int = 0,
    transposition_table: TranspositionTable | None = None,
    qs_tt: TranspositionTable | None = None,
    print_uci: bool = True,
    opening_book: dict = {}
):

    if movetime != 0:

        if board.to_fen(b) in opening_book:
            move = opening_book[board.to_fen(b)]["moves"][0]["move"]
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
                best_node=None,
            )

        start_time = time.time_ns()

        last_search: Search | None = None
        for i in range(1, 10 if max_depth == 0 else max_depth):

            # we create a queue to be able to stop the search when there's no time left
            queue: multiprocessing.Queue[Search | None] = multiprocessing.Queue()
            process = multiprocessing.Process(
                target=search_wrapper,
                args=(queue, b),
                kwargs={
                    "depth": i,
                    "transposition_table": transposition_table,
                    "qs_tt": qs_tt,
                    "alg_fn": alg_fn,
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
                        if print_uci:
                            print("bestmove nomove")
                        return None

                except:
                    current_search = None

                # calculate used time
                used_time = int(max(1, (time.time_ns() - start_time) // 1e9))

                if isinstance(current_search, Search) and current_search is not None:

                    last_search = current_search

                    if print_uci:
                        print(
                            ""
                            + f"info depth {last_search.depth} "
                            + f"score cp {last_search.score} "
                            + f"time {int(last_search.time // 1e9)} "
                            + f"nodes {last_search.nodes} "
                            + (
                                "nps "
                                + str(
                                    int(
                                        last_search.nodes
                                        * 1e9
                                        // max(0.001, last_search.time)
                                    )
                                )
                                + " " if last_search.time > 0 else ""
                            )
                            + f"pv {' '.join([to_uci(x) for x in last_search.pv])}"
                        )

                    # bail out if the search tells us to stop
                    if current_search.stop_search:
                        process.terminate()
                        queue.close()
                        if print_uci:
                            print(f"bestmove {to_uci(current_search.move)}")
                        return last_search

                # bail out if we have a mate
                if last_search is not None and abs(last_search.score) >= VALUE_MAX:
                    if print_uci:
                        print(f"bestmove {to_uci(last_search.move)}")
                    return last_search

                # bail out if we have no time anymore
                if used_time + 1 >= movetime:
                    process.terminate()
                    queue.close()
                    if last_search is not None and print_uci:
                        print(f"bestmove {to_uci(last_search.move)}")
                        return last_search
                    return None
    else:
        last_search = None
        for i in range(1, max_depth + 1):
            current_search = search(
                b,
                depth=i,
                alg_fn=alg_fn,
                transposition_table=transposition_table,
                qs_tt=qs_tt,
                last_search=last_search,
            )

            # if there is no move available
            if current_search is None:
                # This is not strictly UCI but helps for evaluation/versus.py
                if print_uci:
                    print("bestmove nomove")
                return None

            if print_uci:
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

        if last_search is not None and print_uci:
            print(f"bestmove {to_uci(last_search.move)}")
        return last_search
