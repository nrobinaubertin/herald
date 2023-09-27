import pytest
from herald import board, time_management

start_fen = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"]

@pytest.mark.parametrize("movetime,wtime,btime,winc,binc,expected", [
    (1000, 0, 0, 0, 0, 10),  # we expect movetime to take precedence
    (1234, 1, 2, 3, 4, 12),  # we expect movetime to take precedence
    (0, 0, 1, 3, 4, 1),  # we expect at least 1
    (0, 0, 0, 0, 0, 1),  # we expect at least 1
    (0, 60000, 0, 1000, 0, 20),  # we expect to take 2s at the start of the game if we have 1mn
    (0, 60000, 0, 10000, 0, 110),  # we increase thinking time linearly to increment
    (0, 600000, 0, 10000, 0, 150),  # thinking time should not go over 15s
])
def test_time_management_from_start(
    movetime: int,
    wtime: int,
    btime: int,
    winc: int,
    binc: int,
    expected: int,
):
    b = board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0")
    assert time_management.target_movetime(b, movetime, wtime, btime, winc, binc) == expected
