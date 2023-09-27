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
        return int(movetime / 100)

    # the engine doesn't perform well when thinking too long
    max_thinking_time: int = 15000

    # safeguard of 100ms to make our move
    safeguard: int = 100

    if b.turn == COLOR.WHITE:
        remaining_time = wtime
        time_inc = winc
    else:
        remaining_time = btime
        time_inc = binc

    # estimated turns remaining
    remaining_turns = 60 * remaining_material_percent(b.remaining_material)

    time = (
        min(
            remaining_time - safeguard,
            remaining_time / remaining_turns + time_inc,
            max_thinking_time,
        )
    )

    print(
            remaining_time - safeguard,
            remaining_time / remaining_turns + time_inc,
            max_thinking_time,
    )
    print(remaining_time, time_inc, remaining_material_percent(b.remaining_material), remaining_turns, time)

    # we want to return at least 1
    return max(1, int(time / 100))
