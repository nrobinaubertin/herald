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


@pytest.mark.parametrize("fen,expected_pawn_number,expected_pawn_in_file", [
    ("1k6/8/6pp/p3p3/1n1p2PP/4PP2/r2NK3/7R w - - 0 42", [4, 5],
        [
            0, 0, 0, 0, 0, 1, 1, 1, 1, 0,
            0, 1, 0, 0, 1, 1, 0, 1, 1, 0,
        ],
    ),
    ("r1bqr1k1/p2nbppp/2n1p3/PpppP3/3P1P2/2N1BN2/1PP3PP/R2QKB1R w KQ b6 0 11", [8, 8],
        [
            0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
            0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
        ],
    ),
    ("r1bqr1k1/1P1nbppp/2n1p3/p1ppP3/3P1P2/2N1BN2/1PP3PP/R2QKB1R w KQ - 0 13", [8, 7],
        [
            0, 0, 2, 1, 1, 1, 1, 1, 1, 0,
            0, 1, 0, 1, 1, 1, 1, 1, 1, 0,
        ],
    )
])
def test_from_fen(fen, expected_pawn_number, expected_pawn_in_file):
    b = board.from_fen(fen)
    assert b.pawn_number == expected_pawn_number
    assert b.pawn_in_file == expected_pawn_in_file


@pytest.mark.parametrize("fen,uci_move,expected_pawn_number,expected_pawn_in_file", [
    ("1k6/8/6pp/p3p3/1n1p2PP/4PP2/r2NK3/7R w - - 0 42", "e3d4", [4, 4],
        [
            0, 0, 0, 0, 1, 0, 1, 1, 1, 0,
            0, 1, 0, 0, 0, 1, 0, 1, 1, 0,
        ],
    ),
    ("r1bqr1k1/p2nbppp/2n1p3/PpppP3/3P1P2/2N1BN2/1PP3PP/R2QKB1R w KQ b6 0 11", "a5b6", [8, 7],
        [
            0, 0, 2, 1, 1, 1, 1, 1, 1, 0,
            0, 1, 0, 1, 1, 1, 1, 1, 1, 0,
        ],
    ),
    ("r1bqr1k1/1P1nbppp/2n1p3/p1ppP3/3P1P2/2N1BN2/1PP3PP/R2QKB1R w KQ - 0 13", "b7a8", [7, 7],
        [
            0, 0, 1, 1, 1, 1, 1, 1, 1, 0,
            0, 1, 0, 1, 1, 1, 1, 1, 1, 0,
        ],
    ),
    ("r1bqr1k1/1P1nbppp/2n1p3/p1ppP3/3P1P2/2N1BN2/1PP3PP/R2QKB1R w KQ - 0 13", "b7b8", [7, 7],
        [
            0, 0, 1, 1, 1, 1, 1, 1, 1, 0,
            0, 1, 0, 1, 1, 1, 1, 1, 1, 0,
        ],
    )
])
def test_push(
    fen: str,
    uci_move: str,
    expected_pawn_number: list[int],
    expected_pawn_in_file: list[int],
):
    b = board.from_fen(fen)
    move = board.from_uci(b, uci_move)
    nb = board.push(b, move)
    assert nb.pawn_number == expected_pawn_number
    assert nb.pawn_in_file == expected_pawn_in_file
