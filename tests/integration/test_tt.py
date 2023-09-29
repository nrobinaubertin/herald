"""Test transposition table."""

import pytest
from herald.configuration import Config
from herald.constants import VALUE_MAX, COLOR
from herald import alphabeta
from herald import utils

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
    alphabeta_result = alphabeta.alphabeta(
        config=Config(
            quiescence_depth=25,
            quiescence_search=use_qs,
            use_transposition_table=False,
        ),
        b=b,
        depth=depth,
        pv=[],
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    alphabeta_tt_result = alphabeta.alphabeta(
        config=Config(
            quiescence_depth=25,
            quiescence_search=use_qs,
            use_transposition_table=True,
        ),
        b=b,
        depth=depth,
        pv=[],
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    if b.turn == COLOR.WHITE:
        node1 = max(alphabeta_tt_result, key=lambda x: x.value)
        node2 = max(alphabeta_result, key=lambda x: x.value)
        # We cannot be sure that exactly the same line will be selected
        # Only the it will be equivalent in value
        assert node1.value == node2.value, f"{node1.value}, {node2.value}"
    else:
        node1 = min(alphabeta_tt_result, key=lambda x: x.value)
        node2 = min(alphabeta_result, key=lambda x: x.value)
        # We cannot be sure that exactly the same line will be selected
        # Only the it will be equivalent in value
        assert node1.value == node2.value, f"{node1.value}, {node2.value}"
