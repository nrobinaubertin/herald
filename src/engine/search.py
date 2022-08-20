from collections import deque, namedtuple
import time
import random
from .constants import COLOR
from .evaluation import VALUE_MAX
from .board import Board
from .algorithms import alphabeta_mo_tt
from .data_structures import Node
from .transposition_table import TranspositionTable

Search = namedtuple(
    "Search", ["move", "depth", "score", "nodes", "time", "best_node", "pv"]
)


def search(
    board: Board,
    depth: int,
    rand_count: int = 1,
    transposition_table: TranspositionTable = None,
):

    start_time = time.time_ns()

    best = Node(
        depth=depth,
        value=(VALUE_MAX if board.turn == COLOR.BLACK else -VALUE_MAX),
    )
    node_count = 0
    nodes = []

    possible_moves = board.moves()

    # if there's only one move possible, return it immediately
    if len(possible_moves) == 1:
        return Search(
            move=possible_moves[0],
            pv=[possible_moves[0]],
            depth=0,
            nodes=1,
            score=0,
            time=(time.time_ns() - start_time),
            best_node=Node(depth=0, value=0)
        )

    for move in possible_moves:
        curr_board = board.copy()
        curr_board.push(move)
        node = alphabeta_mo_tt(
            curr_board,
            -VALUE_MAX,
            VALUE_MAX,
            depth,
            deque([move]),
            transposition_table=transposition_table,
        )
        node_count += node.children + 1
        nodes.append(Node(depth=depth, value=node.value, pv=node.pv))

    nodes = sorted(nodes, key=lambda x: x.value, reverse=board.turn == COLOR.WHITE)
    best = random.choice(nodes[:rand_count])

    if best is None:
        return None

    return Search(
        move=best.pv[0],
        pv=best.pv,
        depth=depth,
        nodes=node_count,
        score=best.value,
        time=(time.time_ns() - start_time),
        best_node=best,
    )
