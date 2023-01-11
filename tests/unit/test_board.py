import pytest

from herald import board

win_at_chess = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"]

with open("tests/epd/wac.epd", "r") as wacfile:
    for line in wacfile:
        epd = line.split()
        win_at_chess.append(" ".join(epd[:4]) + " 0 0")


@pytest.mark.parametrize("fen", win_at_chess)
def test_fen(fen: str):
    b = board.from_fen(fen)
    assert board.to_fen(b) == fen
