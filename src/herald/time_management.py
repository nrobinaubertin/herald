from .board import Board
from .constants import COLOR, PIECE
from .evaluation import PIECE_VALUE, START_MATERIAL, remaining_material


def target_movetime(
    b: Board,
    movetime: int,
    wtime: int,
    btime: int,
    winc: int,
    binc: int,
) -> int:
    # if movetime is decided, return it immediately
    if movetime > 0:
        return movetime // 1000

    # the engine doesn't perform well when thinking too long
    max_thinking_time: int = 15000

    if b.turn == COLOR.WHITE:
        remaining_time = wtime
        time_inc = winc
    else:
        remaining_time = btime
        time_inc = binc

    # percent of the game by material
    p = (remaining_material(b) - PIECE_VALUE[PIECE.KING] * 2) / (
        START_MATERIAL - PIECE_VALUE[PIECE.KING] * 2
    )

    # estimated turns remaining
    t = 40 * p

    time = (
        min(
            remaining_time - 1,
            remaining_time / t + 2 * time_inc,
            max_thinking_time,
        )
        / 1000
    )

    return int(time)
