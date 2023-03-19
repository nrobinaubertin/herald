from .board import Board
from .constants import COLOR
from .evaluation import remaining_material_percent


def target_movetime(
    b: Board,
    movetime: int,
    wtime: int,
    btime: int,
    winc: int,
    binc: int,
) -> int:
    """Return target maximum movetime in deciseconds."""
    # if movetime is decided, return it immediately
    if movetime > 0:
        return movetime // 100

    # the engine doesn't perform well when thinking too long
    max_thinking_time: int = 15000

    if b.turn == COLOR.WHITE:
        remaining_time = wtime
        time_inc = winc
    else:
        remaining_time = btime
        time_inc = binc

    # estimated turns remaining
    t = 40 * remaining_material_percent(b.remaining_material)

    time = (
        min(
            remaining_time - 1,
            remaining_time / t + 2 * time_inc,
            max_thinking_time,
        )
        / 100
    )

    return int(time)
