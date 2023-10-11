"""Test transposition table."""

import pytest
from configuration import Config
from constants import VALUE_MAX
import alphabeta
import utils

fens = []
with open("tests/epd/transposition_table.epd", "r") as tt_file:
    for line in tt_file:
        epd = line.split()
        fens.append(" ".join(epd[:4]) + " 0 0")


# This test equivalence between w/ and w/o tt
@pytest.mark.parametrize("fen", fens)
@pytest.mark.parametrize("depth", (3, 4, 5, 6))
@pytest.mark.parametrize("use_qs", (True, False))
def test_tt_equivalence(fen, depth, use_qs):
    b = utils.from_fen(fen)
    pv1 = []
    alphabeta_result = alphabeta.alphabeta(
        config=Config(
            quiescence_depth=25,
            quiescence_search=use_qs,
            use_transposition_table=False,
        ),
        b=b,
        depth=depth,
        pv=pv1,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    pv2 = []
    alphabeta_tt_result = alphabeta.alphabeta(
        config=Config(
            quiescence_depth=25,
            quiescence_search=use_qs,
            use_transposition_table=True,
        ),
        b=b,
        depth=depth,
        pv=pv2,
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    assert alphabeta_tt_result == alphabeta_result, (
        f"{alphabeta_tt_result} "
        f"{','.join([utils.to_uci(x) for x in pv1])}, "
        f"{alphabeta_result} "
        f"{','.join([utils.to_uci(x) for x in pv2])}"
    )
