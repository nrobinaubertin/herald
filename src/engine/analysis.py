import json
from .algorithms import Alg_fn
from collections import deque
from .transposition_table import TranspositionTable
from .constants import COLOR, VALUE_MAX
from . import board
from .evaluation import eval_simple
from .data_structures import Board, to_uci
from . import move_ordering


def fen_analysis(
    input,
    output,
    alg_fn: Alg_fn,
    depth: int = 0,
    branch_factor: int = 1,
    transposition_table: TranspositionTable | None = None,
):
    fens = []
    with open(input, "r") as input_file:
        fens = [x for x in input_file.readlines()]

    data = {}
    with open(output, "r") as output_file:
        data = json.load(output_file)

    for fen in fens:
        fen = fen.strip()
        # ignore fens already precomputed
        if (
            fen in data
            and data[fen]["depth"] >= depth
            and len(data[fen]["moves"]) >= branch_factor
        ):
            continue
        b = board.from_fen(fen)
        moves = analysis(b, alg_fn, depth, branch_factor, transposition_table)
        data[fen] = {
            "depth": depth,
            "moves": moves,
        }
        print(f"{fen}: {','.join([to_uci(x['move']) for x in moves])}")

        # dump intermediary result
        with open(output, "w") as output_file:
            json.dump(data, output_file)

        # add new positions to the list of fens to analyse
        for move in [x["move"] for x in moves]:
            nb = board.push(b, move)
            fens.append(board.to_fen(nb))

    print("Done!")


def analysis(
    b: Board,
    alg_fn: Alg_fn,
    depth: int = 0,
    branch_factor: int = 1,
    transposition_table: TranspositionTable | None = None,
):

    results = []

    possible_moves = [x for x in board.legal_moves(b)]

    if len(possible_moves) == 0:
        return []

    # if there's only one move possible, return it immediately
    if len(possible_moves) == 1:
        results.append({
            "move": possible_moves[0],
            "score": 0,
        })
        return results

    # Assume that we are not in zugzwang and that we can find a move that improves the situation
    if b.turn == COLOR.WHITE:
        alpha: int = eval_simple(b)
        beta: int = VALUE_MAX
    else:
        alpha: int = -VALUE_MAX
        beta: int = eval_simple(b)

    children: int = 1

    for move in possible_moves:

        node = alg_fn(
            board.push(b, move),
            depth,
            deque([move]),
            eval_simple,
            alpha,
            beta,
            transposition_table,
            move_ordering.mvv_lva,
        )

        children += node.children

        results.append({
            "move": node.pv[0],
            "score": node.value,
        })

    return sorted(
        results,
        key=lambda x: x["score"],
        reverse=(b.turn == COLOR.WHITE)
    )[:branch_factor]
