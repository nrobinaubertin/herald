"""Test algorithms equivalence.

We test algorithms by comparing results to the minimax algorithm who's well known.
When comparing move ordering functions, we cannot compare pvs
"""

import pytest

from configuration import Config
from constants import VALUE_MAX, COLOR_DIRECTION
import utils
import search

import minimax
import alphabeta
import negamax
import negamax_mo

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


# This test equivalence between alphabeta and minimax
@pytest.mark.parametrize("fen", fens)
@pytest.mark.parametrize("depth", (1, 2, 3))
def test_alphabeta(fen, depth):
    b = utils.from_fen(fen)
    pv1 = []
    r1 = minimax.minimax(
        b=b,
        depth=depth,
        pv=pv1,
        gen_legal_moves=False,
    )
    pv2 = []
    r2 = alphabeta.alphabeta(
        b=b,
        depth=depth,
        pv=pv2,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    assert r1 == r2, (
        f"{fen}: "
        f"{','.join([utils.to_uci(x) for x in pv1])} "
        f"{fen}: {','.join([utils.to_uci(x) for x in pv2])}"
    )
    assert (
        f"{fen}: {','.join([utils.to_uci(x) for x in pv1])}"
        == f"{fen}: {','.join([utils.to_uci(x) for x in pv2])}"
    )


# This test equivalence between alphabeta and negamax
@pytest.mark.parametrize("fen", fens)
@pytest.mark.parametrize("depth", (1, 2, 3, 4))
def test_negamax(fen, depth):
    b = utils.from_fen(fen)
    pv1 = []
    r1 = alphabeta.alphabeta(
        b=b,
        depth=depth,
        pv=pv1,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    pv2 = []
    r2 = negamax.negamax(
        b=b,
        depth=depth,
        pv=pv2,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    ) * COLOR_DIRECTION[b.turn]
    assert r1 == r2, (
        f"{fen}: "
        f"{','.join([utils.to_uci(x) for x in pv1])} "
        f"{fen}: {','.join([utils.to_uci(x) for x in pv2])}"
    )
    assert (
        f"{fen}: {','.join([utils.to_uci(x) for x in pv1])}"
        == f"{fen}: {','.join([utils.to_uci(x) for x in pv2])}"
    )


# This test equivalence between negamax and negamax with move ordering
@pytest.mark.parametrize("fen", fens)
@pytest.mark.parametrize("depth", (1, 2, 3, 4))
def test_negamax_mo(fen, depth):
    b = utils.from_fen(fen)
    pv1 = []
    r1 = negamax_mo.negamax_mo(
        b=b,
        depth=depth,
        pv=pv1,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    ) * COLOR_DIRECTION[b.turn]
    pv2 = []
    r2 = negamax.negamax(
        b=b,
        depth=depth,
        pv=pv2,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    ) * COLOR_DIRECTION[b.turn]
    assert r1 == r2, (
        f"{fen}: "
        f"{','.join([utils.to_uci(x) for x in pv1])} "
        f"{fen}: {','.join([utils.to_uci(x) for x in pv2])}"
    )
    # We cannot compare PVs since move ordering can affect it.
    # Multiple PVs can have the same evaluation
    # assert (
    #     f"{fen}: {','.join([utils.to_uci(x) for x in pv1])}"
    #     == f"{fen}: {','.join([utils.to_uci(x) for x in pv2])}"
    # )


# This test equivalence between our search and negamax_mo
@pytest.mark.parametrize("fen", fens)
@pytest.mark.parametrize("depth", (1, 2, 3, 4, 5))
def test_search(fen, depth):
    b = utils.from_fen(fen)
    pv1 = []
    r1 = negamax_mo.negamax_mo(
        b=b,
        depth=depth,
        pv=pv1,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    ) * COLOR_DIRECTION[b.turn]
    pv2 = []
    r2 = search.alphabeta(
        config=Config(
            use_transposition_table=False,
            quiescence_search=False,
            use_hash_move=False,
        ),
        b=b,
        depth=depth,
        pv=pv2,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    assert r1 == r2, (
        f"{fen}: "
        f"{','.join([utils.to_uci(x) for x in pv1])} "
        f"{fen}: {','.join([utils.to_uci(x) for x in pv2])}"
    )
    # assert (
    #     f"{fen}: {','.join([utils.to_uci(x) for x in pv1])}"
    #     == f"{fen}: {','.join([utils.to_uci(x) for x in pv2])}"
    # )


# @pytest.mark.parametrize("fen", fens[:25])
# @pytest.mark.parametrize("depth", (3, 4))
# def test_hash_move(fen, depth):
#     pv1 = []
#     r1 = search.alphabeta(
#         config=Config(
#             quiescence_depth=50,
#             quiescence_search=True,
#             use_transposition_table=True,
#             use_hash_move=True,
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
#             use_hash_move=False,
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
