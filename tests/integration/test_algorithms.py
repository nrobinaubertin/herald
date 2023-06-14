"""Test algorithms equivalence.

We test algorithms by comparing results to the minimax algorithm who's well known.
When comparing move ordering functions, we cannot compare pvs
"""

import pytest
from herald import algorithms, board, move_ordering, quiescence
from herald.algorithms import alphabeta
from herald.minimax import minimax
from herald.configuration import Config
from herald.constants import VALUE_MAX
from herald.data_structures import to_uci

win_at_chess = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"]
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
    r1 = alphabeta(
        config=Config(
            alg_fn=algorithms.alphabeta,
            move_ordering_fn=move_ordering.no_ordering,
            quiescence_fn=quiescence.quiescence,
            use_transposition_table=False,
        ),
        b=board.from_fen(fen),
        depth=depth,
        pv=[],
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    r2 = alphabeta(
        config=Config(
            alg_fn=algorithms.alphabeta,
            move_ordering_fn=move_ordering.fast_ordering,
            quiescence_fn=quiescence.quiescence,
            use_transposition_table=False,
        ),
        b=board.from_fen(fen),
        depth=depth,
        pv=[],
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    n1 = max(r1, key=lambda x: x.value)
    n2 = max(r2, key=lambda x: x.value)
    assert n1.value == n2.value
    # The fast ordering function can return different moves as long
    # as their value is the same. That means that we cannot test the pv equivalence
    # assert (
    #     f"{fen}: {','.join([to_uci(x) for x in n1.pv])}"
    #     == f"{fen}: {','.join([to_uci(x) for x in n2.pv])}"
    # )


# This test equivalence between raw alphabeta and minimax
@pytest.mark.parametrize("fen", fens[:25])
@pytest.mark.parametrize("depth", (1, 2, 3))
def test_alphabeta(fen, depth):
    r1 = minimax(
        Config(
            alg_fn=minimax,
            move_ordering_fn=move_ordering.no_ordering,
            quiescence_fn=quiescence.quiescence,
            use_transposition_table=False,
        ),
        board.from_fen(fen),
        depth,
        [],
        False,
    )
    r2 = alphabeta(
        config=Config(
            alg_fn=algorithms.alphabeta,
            move_ordering_fn=move_ordering.no_ordering,
            quiescence_fn=quiescence.quiescence,
            use_transposition_table=False,
        ),
        b=board.from_fen(fen),
        depth=depth,
        pv=[],
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    n1 = r1
    n2 = max(r2, key=lambda x: x.value)
    assert n1.value == n2.value
    assert (
        f"{fen}: {','.join([to_uci(x) for x in n1.pv])}"
        == f"{fen}: {','.join([to_uci(x) for x in n2.pv])}"
    )


@pytest.mark.parametrize("fen", fens[:25])
@pytest.mark.parametrize("depth", (3, 4))
def test_hash_move(fen, depth):
    r1 = alphabeta(
        config=Config(
            alg_fn=algorithms.alphabeta,
            move_ordering_fn=move_ordering.fast_ordering,
            quiescence_depth=50,
            quiescence_fn=quiescence.quiescence,
            quiescence_search=True,
            use_transposition_table=True,
        ),
        b=board.from_fen(fen),
        depth=depth,
        pv=[],
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    r2 = alphabeta(
        config=Config(
            alg_fn=algorithms.alphabeta,
            move_ordering_fn=move_ordering.fast_ordering,
            quiescence_depth=50,
            quiescence_fn=quiescence.quiescence,
            quiescence_search=True,
            use_transposition_table=True,
        ),
        b=board.from_fen(fen),
        depth=depth,
        pv=[],
        gen_legal_moves=False,
        alpha=-VALUE_MAX,
        beta=VALUE_MAX,
    )
    n1 = max(r1, key=lambda x: x.value)
    n2 = max(r2, key=lambda x: x.value)
    assert n1.value == n2.value
    assert (
        f"{fen}: {','.join([to_uci(x) for x in n1.pv])}"
        == f"{fen}: {','.join([to_uci(x) for x in n2.pv])}"
    )
