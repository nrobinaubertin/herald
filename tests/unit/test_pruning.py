import pytest
import pruning, utils
from constants import COLOR_DIRECTION


@pytest.mark.parametrize(
    "fen, target, bad_capture",
    [
        ("8/p7/1b6/8/8/8/1Q6/8 w - - 0 1", 42, True),
        ("8/p7/1b6/8/8/4Q3/8/8 w - - 0 1", 42, True),
        ("8/3n4/1b6/8/8/4Q3/1R6/8 w - - 0 1", 42, False),
        ("3q3b/3r4/2n5/8/3B4/8/4N3/3R2Q1 b - - 0 1", 64, False),
        ("3r3b/3q4/2n5/8/3B4/8/4N3/3R2Q1 b - - 0 1", 64, False),
        ("2br4/3q4/2n5/8/3R4/8/4N3/3R2Q1 w - - 0 1", 64, False),
        ("2br4/3q4/2n5/8/3R4/8/4N3/3R2Q1 b - - 0 1", 64, False),
        ("2br4/3q4/8/8/3R4/8/4N3/3R2Q1 b - - 0 1", 64, True),
    ],
)
def test_see(fen: str, target: int, bad_capture: bool):
    b = utils.from_fen(fen)
    assert bool(pruning.see(b, target, 0) * COLOR_DIRECTION[b.turn] <= 0) == bad_capture
