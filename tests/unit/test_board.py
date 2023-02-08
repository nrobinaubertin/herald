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


# fmt: off
@pytest.mark.parametrize(
    "fen,expected_pawn_number,expected_pawn_in_file",
    [
        (
            "1k6/8/6pp/p3p3/1n1p2PP/4PP2/r2NK3/7R w - - 0 42",
            [4, 5],
            [
                0, 0, 0, 0, 0, 1, 1, 1, 1, 0,
                0, 1, 0, 0, 1, 1, 0, 1, 1, 0,
            ],
        ),
        (
            "r1bqr1k1/p2nbppp/2n1p3/PpppP3/3P1P2/2N1BN2/1PP3PP/R2QKB1R w KQ b6 0 11",
            [8, 8],
            [
                0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
                0, 1, 1, 1, 1, 1, 1, 1, 1, 0,
            ],
        ),
        (
            "r1bqr1k1/1P1nbppp/2n1p3/p1ppP3/3P1P2/2N1BN2/1PP3PP/R2QKB1R w KQ - 0 13",
            [8, 7],
            [
                0, 0, 2, 1, 1, 1, 1, 1, 1, 0,
                0, 1, 0, 1, 1, 1, 1, 1, 1, 0,
            ],
        ),
    ],
)
# fmt: on
def test_from_fen(fen, expected_pawn_number, expected_pawn_in_file):
    b = board.from_fen(fen)
    assert b.pawn_number == expected_pawn_number
    assert b.pawn_in_file == expected_pawn_in_file


# fmt: off
@pytest.mark.parametrize(
    "fen,uci_move,expected_pawn_number,expected_pawn_in_file",
    [
        (
            "1k6/8/6pp/p3p3/1n1p2PP/4PP2/r2NK3/7R w - - 0 42",
            "e3d4",
            [4, 4],
            [
                0, 0, 0, 0, 1, 0, 1, 1, 1, 0,
                0, 1, 0, 0, 0, 1, 0, 1, 1, 0,
            ],
        ),
        (
            "r1bqr1k1/p2nbppp/2n1p3/PpppP3/3P1P2/2N1BN2/1PP3PP/R2QKB1R w KQ b6 0 11",
            "a5b6",
            [8, 7],
            [
                0, 0, 2, 1, 1, 1, 1, 1, 1, 0,
                0, 1, 0, 1, 1, 1, 1, 1, 1, 0,
            ],
        ),
        (
            "r1bqr1k1/1P1nbppp/2n1p3/p1ppP3/3P1P2/2N1BN2/1PP3PP/R2QKB1R w KQ - 0 13",
            "b7a8",
            [7, 7],
            [
                0, 0, 1, 1, 1, 1, 1, 1, 1, 0,
                0, 1, 0, 1, 1, 1, 1, 1, 1, 0,
            ],
        ),
        (
            "r1bqr1k1/1P1nbppp/2n1p3/p1ppP3/3P1P2/2N1BN2/1PP3PP/R2QKB1R w KQ - 0 13",
            "b7b8",
            [7, 7],
            [
                0, 0, 1, 1, 1, 1, 1, 1, 1, 0,
                0, 1, 0, 1, 1, 1, 1, 1, 1, 0,
            ],
        ),
    ],
)
# fmt: on
def test_push_pawn(
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


@pytest.mark.parametrize(
    "fen,uci_moves,expected_fen",
    [
        ("startpos", "d2d4", "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq d3 0 1"),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3",
            "r2qkbnr/ppp1pppp/2n5/3p1b2/3P1B2/4PN2/PPP2PPP/RN1QKB1R b KQkq - 0 4",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3",
            "r2qkb1r/ppp1pppp/2n2n2/3p1b2/3P1B2/3BPN2/PPP2PPP/RN1QK2R b KQkq - 2 5",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3",
            "r2qkb1r/ppp1pppp/2n2n2/3p4/3P1B2/3bPN2/PPP2PPP/RN1QK2R w KQkq - 0 6",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3",
            "r2qkb1r/ppp1pppp/2n2n2/3p4/3P1B2/3QPN2/PPP2PPP/RN2K2R b KQkq - 0 6",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3",
            "r2qkb1r/ppp1pppp/2n5/3p3n/3P4/3QPNB1/PPP2PPP/RN2K2R b KQkq - 2 7",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3,h5g3",
            "r2qkb1r/ppp1pppp/2n5/3p4/3P4/3QPNn1/PPP2PPP/RN2K2R w KQkq - 0 8",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3,h5g3,h2g3",
            "r2qkb1r/ppp1pppp/2n5/3p4/3P4/3QPNP1/PPP2PP1/RN2K2R b KQkq - 0 8",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3,h5g3,h2g3,d8d7,h1h7,c6b4,h7h8,b4d3,c2d3,d7b5,b2b3,b5d3,b1d2",
            "r3kb1R/ppp1ppp1/8/3p4/3P4/1P1qPNP1/P2N1PP1/R3K3 b Qq - 1 13",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3,h5g3,h2g3,d8d7,h1h7,c6b4,h7h8,b4d3,c2d3,d7b5,b2b3,b5d3,b1d2,f7f6,a1c1,e8c8,e1d1,c8b8,c1c2,e7e5,d4e5,d8e8",
            "1k2rb1R/ppp3p1/5p2/3pP3/8/1P1qPNP1/P1RN1PP1/3K4 w - - 1 18",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3,h5g3,h2g3,d8d7,h1h7,c6b4,h7h8,b4d3,c2d3,d7b5,b2b3,b5d3,b1d2,f7f6,a1c1,e8c8,e1d1,c8b8,c1c2,e7e5,d4e5,d8e8,e5f6,g7f6,f3e1,d3g6,h8h4,f8d6,d1e2,b8c8,e1d3",
            "2k1r3/ppp5/3b1pq1/3p4/7R/1P1NP1P1/P1RNKPP1/8 b - - 7 22",
        ),
    ],
)
def test_push_from_fen(
    fen: str,
    uci_moves: str,
    expected_fen: str,
):
    b = board.from_fen(fen)
    for uci_move in uci_moves.split(","):
        move = board.from_uci(b, uci_move)
        b = board.push(b, move)
    expected = board.from_fen(expected_fen)
    for k in b.__dict__:
        assert expected.__dict__.get(k) == b.__dict__.get(k)
    assert board.to_fen(b) == expected_fen
