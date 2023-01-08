import pytest
from herald import board

from ..win_at_chess import win_at_chess


@pytest.mark.parametrize("fen", win_at_chess)
def test_fen(fen: str):
    b = board.from_fen(fen)
    assert board.to_fen(b) == fen
