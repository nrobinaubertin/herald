from .constants import COLOR

# the engine doesn't perform well when thinking too long
MAX_THINKING_TIME: int = 15000


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
        time = (
            min(
                wtime,
                wtime // 40 + 3 * winc,
                MAX_THINKING_TIME,
            )
            // 1000
        )
    else:
        time = (
            min(
                btime - 1,
                btime // 40 + 3 * binc,
                MAX_THINKING_TIME,
            )
            // 1000
        )

    return time - 1
