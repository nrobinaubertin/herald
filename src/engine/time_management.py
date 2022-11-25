from .constants import COLOR

# the engine doesn't perform well when thinking over 20s
MAX_THINKING_TIME: int = 20000


def target_movetime(
    turn: COLOR,
    movetime: int,
    wtime: int,
    btime: int,
    winc: int,
    binc: int,
) -> int:
    if movetime > 0:
        return movetime // 1000

    if turn == COLOR.WHITE:
        time = min(
            wtime,
            wtime // 40 + 4 * winc,
            MAX_THINKING_TIME,
        ) // 1000
    else:
        time = min(
            btime,
            btime // 40 + 4 * binc,
            MAX_THINKING_TIME,
        ) // 1000

    return time


# This function should evaluate if we have time to think deeper
def is_there_time(
    used_time: int,
    remaining_time: int,
    inc_time: int,
    print_uci: bool = False,
) -> bool:

    # fail-safe if there's no time left
    if remaining_time < 2:
        if print_uci:
            print("info no time left")
        return False

    if (
        (remaining_time - inc_time) // 20 < used_time - inc_time
        and used_time + 1 > inc_time
    ):
        if print_uci:
            print("info no time for next depth")
        return False

    return True
