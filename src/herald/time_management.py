from .constants import COLOR
from .board import Board
from .evaluation import START_MATERIAL, remaining_material, PIECE_VALUE, PIECE


def target_movetime(
    b: Board,
    movetime: int,
    wtime: int,
    btime: int,
    winc: int,
    binc: int,
) -> int:

    # if movetime is decided, return it immediatly
    if movetime > 0:
        return movetime // 1000

    # the engine doesn't perform well when thinking too long
    MAX_THINKING_TIME: int = 15000

    if b.turn == COLOR.WHITE:
        remaining_time = wtime
        time_inc = winc
    else:
        remaining_time = btime
        time_inc = binc

    # percent of the game by material
    p = (remaining_material(b) - PIECE_VALUE[PIECE.KING] * 2) / (START_MATERIAL - PIECE_VALUE[PIECE.KING] * 2)

    # estimated turns remaining
    t = 60 * p

    time = (
        min(
            remaining_time,
            (remaining_time + 3 * time_inc) / t,
            MAX_THINKING_TIME,
        )
        / 1000
    )

    return int(time)
