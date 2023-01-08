import json
from collections import deque
from operator import itemgetter

from herald import board
from herald.constants import COLOR, VALUE_MAX
from herald.data_structures import Board, MoveType, to_uci


def fen_analysis(
    config,
    input,
    output,
    depth: int = 0,
    branch_factor: int = 1,
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
        moves = analysis(config, b, depth, branch_factor)
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
    config,
    b: Board,
    depth: int = 0,
    branch_factor: int = 1,
):

    results = []

    possible_moves = [x for x in board.legal_moves(b)]

    if len(possible_moves) == 0:
        return []

    # if there's only one move possible, return it immediately
    if len(possible_moves) == 1:
        results.append(
            {
                "move": possible_moves[0],
                "score": 0,
            }
        )
        return results

    children: int = 1

    for move in possible_moves:

        node = config.alg_fn(
            config,
            board.push(b, move),
            depth - 1,
            deque([move]),
            MoveType.LEGAL,
            -VALUE_MAX,
            VALUE_MAX,
        )

        children += node.children

        results.append(
            {
                "move": node.pv[0],
                "score": node.value,
            }
        )

    return sorted(results, key=itemgetter("score"), reverse=(b.turn == COLOR.WHITE))[
        :branch_factor
    ]
