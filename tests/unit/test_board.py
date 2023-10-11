import pytest
import board, utils, constants

win_at_chess = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"]

with open("tests/epd/wac.epd", "r") as wacfile:
    for line in wacfile:
        epd = line.split()
        win_at_chess.append(" ".join(epd[:4]) + " 0 0")


@pytest.mark.parametrize("fen", win_at_chess)
def test_fen(fen: str):
    b = utils.from_fen(fen)
    assert utils.to_fen(b) == fen


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
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3,h5g3,h2g3,d8d7,h1h7,c6b4,h7h8,b4d3,c2d3,d7b5,b2b3,b5d3,b1d2,f7f6",
            "r3kb1R/ppp1p1p1/5p2/3p4/3P4/1P1qPNP1/P2N1PP1/R3K3 w Qq - 0 14",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3,h5g3,h2g3,d8d7,h1h7,c6b4,h7h8,b4d3,c2d3,d7b5,b2b3,b5d3,b1d2,f7f6,a1c1",
            "r3kb1R/ppp1p1p1/5p2/3p4/3P4/1P1qPNP1/P2N1PP1/2R1K3 b q - 1 14",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3,h5g3,h2g3,d8d7,h1h7,c6b4,h7h8,b4d3,c2d3,d7b5,b2b3,b5d3,b1d2,f7f6,a1c1,e8c8",
            "2kr1b1R/ppp1p1p1/5p2/3p4/3P4/1P1qPNP1/P2N1PP1/2R1K3 w - - 2 15",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3,h5g3,h2g3,d8d7,h1h7,c6b4,h7h8,b4d3,c2d3,d7b5,b2b3,b5d3,b1d2,f7f6,a1c1,e8c8,e1d1",
            "2kr1b1R/ppp1p1p1/5p2/3p4/3P4/1P1qPNP1/P2N1PP1/2RK4 b - - 3 15",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3,h5g3,h2g3,d8d7,h1h7,c6b4,h7h8,b4d3,c2d3,d7b5,b2b3,b5d3,b1d2,f7f6,a1c1,e8c8,e1d1,c8b8",
            "1k1r1b1R/ppp1p1p1/5p2/3p4/3P4/1P1qPNP1/P2N1PP1/2RK4 w - - 4 16",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3,h5g3,h2g3,d8d7,h1h7,c6b4,h7h8,b4d3,c2d3,d7b5,b2b3,b5d3,b1d2,f7f6,a1c1,e8c8,e1d1,c8b8,c1c2",
            "1k1r1b1R/ppp1p1p1/5p2/3p4/3P4/1P1qPNP1/P1RN1PP1/3K4 b - - 5 16",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3,h5g3,h2g3,d8d7,h1h7,c6b4,h7h8,b4d3,c2d3,d7b5,b2b3,b5d3,b1d2,f7f6,a1c1,e8c8,e1d1,c8b8,c1c2,e7e5",
            "1k1r1b1R/ppp3p1/5p2/3pp3/3P4/1P1qPNP1/P1RN1PP1/3K4 w - e6 0 17",
        ),
        (
            "startpos",
            "d2d4,b8c6,g1f3,d7d5,c1f4,c8f5,e2e3,g8f6,f1d3,f5d3,d1d3,f6h5,f4g3,h5g3,h2g3,d8d7,h1h7,c6b4,h7h8,b4d3,c2d3,d7b5,b2b3,b5d3,b1d2,f7f6,a1c1,e8c8,e1d1,c8b8,c1c2,e7e5,d4e5",
            "1k1r1b1R/ppp3p1/5p2/3pP3/8/1P1qPNP1/P1RN1PP1/3K4 b - - 0 17",
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
    b = utils.from_fen(fen)
    for uci_move in uci_moves.split(","):
        move = utils.from_uci(b, uci_move)
        b = board.push(b, move)
    expected = utils.from_fen(expected_fen)
    assert utils.to_fen(b) == expected_fen
    for k in b.__dict__:
        # we can't get king_en_passant from fen alone
        if k == "king_en_passant":
            continue
        assert (k, expected.__dict__.get(k)) == (k, b.__dict__.get(k))


@pytest.mark.parametrize(
    "fen,uci_moves",
    [
        (
            "startpos",
            "a2a3,a2a4,b2b3,b2b4,c2c3,c2c4,d2d3,d2d4,e2e3,e2e4,f2f3,f2f4,g2g3,g2g4,h2h3,h2h4,b1c3,b1a3,g1h3,g1f3",
        ),
        (
            "3r1r1k/p3bPpp/2bp4/5R2/1q1Bn3/1Bp5/PPP3PP/1K1R1Q2 w - - 0 20",
            "f5g5,f5h5,f5e5,f5d5,f5c5,f5b5,f5a5,f5f4,f5f3,f5f2,f5f6,d4e3,d4f2,d4g1,d4c5,d4b6,d4a7,d4c3,d4e5,d4f6,d4g7,b3a4,b3c4,b3d5,b3e6,a2a3,a2a4,b2c3,g2g3,g2g4,h2h3,h2h4,b1c1,b1a1,d1e1,d1c1,d1d2,d1d3,f1e2,f1d3,f1c4,f1b5,f1a6,f1g1,f1h1,f1e1,f1f2,f1f3,f1f4",
        ),
    ],
)
def test_gen_moves(
    fen: str,
    uci_moves: str,
):
    b = utils.from_fen(fen)
    legal_moves = {utils.to_uci(m) for m in board.legal_moves(b)}
    expected_moves = set(uci_moves.split(","))
    assert legal_moves == expected_moves


@pytest.mark.parametrize(
    "fen, square, color, expected",
    [
        (
            "5k2/6pp/p7/3p4/2pP4/2PKP2Q/PP3r2/3R4 w - - 0 3",
            74,
            constants.COLOR.BLACK,
            True,
        ),
        (
            "5k2/6pp/p7/3p4/2pP4/2PKP2Q/PP3r2/3R4 w - - 0 3",
            72,
            constants.COLOR.BLACK,
            True,
        ),
        (
            "5k2/6pp/p7/3p4/2pP4/2PKP2Q/PP3r2/3R4 w - - 0 3",
            71,
            constants.COLOR.WHITE,
            True,
        ),
        (
            "5k2/6pp/p7/3p4/2pP4/2PKP2Q/PP3r2/3R4 w - - 0 3",
            34,
            constants.COLOR.WHITE,
            True,
        ),
        (
            "5k2/6pp/p7/3p4/2pP4/2PKP2Q/PP3r2/3R4 w - - 0 3",
            44,
            constants.COLOR.WHITE,
            False,
        ),
    ],
)
def test_is_square_attacked(
    fen: str,
    square: int,
    color: constants.COLOR,
    expected: bool,
):
    b = utils.from_fen(fen)
    assert expected == board.is_square_attacked(b.squares, square, color)
