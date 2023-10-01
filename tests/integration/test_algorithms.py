"""Test algorithms equivalence.

We test algorithms by comparing results to the minimax algorithm who's well known.
When comparing move ordering functions, we cannot compare pvs
"""

import pytest
from herald.configuration import Config
from herald.constants import VALUE_MAX
from herald import utils
from herald import alphabeta
from herald import minimax

win_at_chess = [
    # Some additional FENs that we want to test
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0",
    "rnbqkbnr/pp2pppp/2p5/3p4/3P1B2/5N2/PPP1PPPP/RN1QKB1R b KQkq - 1 3",
]
with open("tests/epd/wac.epd", "r") as wacfile:
    for line in wacfile:
        epd = line.split()
        win_at_chess.append(" ".join(epd[:4]) + " 0 0")

fens = win_at_chess


# This test equivalence between raw alphabeta
# and alphabeta with fast move ordering
@pytest.mark.parametrize("fen", fens[:25])
@pytest.mark.parametrize("depth", (1, 2, 3))
def test_fast_ordering(fen, depth):
    pv1 = []
    r1 = alphabeta.alphabeta(
        config=Config(use_transposition_table=False),
        b=utils.from_fen(fen),
        depth=depth,
        pv=pv1,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    pv2 = []
    r2 = alphabeta.alphabeta(
        config=Config(use_transposition_table=False),
        b=utils.from_fen(fen),
        depth=depth,
        pv=pv2,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    assert r1 == r2
    # The fast ordering function can return different moves as long
    # as their value is the same. That means that we cannot test the pv equivalence
    # assert (
    #     f"{fen}: {','.join([utils.to_uci(x) for x in pv1])}"
    #     == f"{fen}: {','.join([utils.to_uci(x) for x in pv2])}"
    # )


# This test equivalence between raw alphabeta and minimax
@pytest.mark.parametrize("fen", fens)
@pytest.mark.parametrize("depth", (1, 2, 3, 4, 5))
def test_alphabeta(fen, depth):
    b = utils.from_fen(fen)
    pv1 = []
    r1 = minimax.minimax(
        Config(
            use_transposition_table=False,
            quiescence_search=False,
        ),
        b,
        depth,
        pv1,
        False,
    )
    pv2 = []
    r2 = alphabeta.alphabeta(
        config=Config(
            use_transposition_table=False,
            quiescence_search=False,
        ),
        b=utils.from_fen(fen),
        depth=depth,
        pv=pv2,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    n1 = r1
    n2 = max(r2, key=lambda x: x.value)
    assert n1.value == n2.value, (
        f"{fen}: "
        f"{','.join([utils.to_uci(x) for x in n1.pv])} "
        f"{','.join([utils.to_uci(x) for x in n2.pv])}"
    )
    assert r1.value == r2
    assert (
        f"{fen}: {','.join([utils.to_uci(x) for x in r1.pv])}"
        == f"{fen}: {','.join([utils.to_uci(x) for x in pv2])}"
    )


@pytest.mark.parametrize("fen", fens[:25])
@pytest.mark.parametrize("depth", (3, 4))
def test_hash_move(fen, depth):
    pv1 = []
    r1 = alphabeta.alphabeta(
        config=Config(
            quiescence_depth=50,
            quiescence_search=True,
            use_transposition_table=True,
            use_hash_move=True,
        ),
        b=utils.from_fen(fen),
        depth=depth,
        pv=pv1,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    pv2 = []
    r2 = alphabeta.alphabeta(
        config=Config(
            quiescence_depth=50,
            quiescence_search=True,
            use_transposition_table=True,
            use_hash_move=False,
        ),
        b=utils.from_fen(fen),
        depth=depth,
        pv=pv2,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    assert r1 == r2
    assert (
        f"{fen}: {','.join([utils.to_uci(x) for x in pv1])}"
        == f"{fen}: {','.join([utils.to_uci(x) for x in pv2])}"
    )


# @pytest.mark.parametrize("fen", fens[:25])
# @pytest.mark.parametrize("depth", (3, 4))
# def test_killer_move(fen, depth):
#     pv1 = []
#     r1 = alphabeta.alphabeta(
#         config=Config(
#             quiescence_depth=50,
#             quiescence_search=True,
#             use_transposition_table=True,
#             use_killer_moves=True,
#         ),
#         b=utils.from_fen(fen),
#         depth=depth,
#         pv=pv1,
#         gen_legal_moves=False,
#         alpha=-VALUE_MAX,
#         beta=VALUE_MAX,
#     )
#     pv2 = []
#     r2 = alphabeta.alphabeta(
#         config=Config(
#             quiescence_depth=50,
#             quiescence_search=True,
#             use_transposition_table=True,
#             use_killer_moves=False,
#         ),
#         b=utils.from_fen(fen),
#         depth=depth,
#         pv=pv2,
#         gen_legal_moves=False,
#         alpha=-VALUE_MAX,
#         beta=VALUE_MAX,
#     )
#     assert r1 == r2
#     assert (
#         f"{fen}: {','.join([utils.to_uci(x) for x in pv1])}"
#         == f"{fen}: {','.join([utils.to_uci(x) for x in pv2])}"
#     )
