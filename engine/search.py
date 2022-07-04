from collections import deque, namedtuple
import time
from engine.constants import COLOR
from engine.evaluation import VALUE_MAX, eval_board
from engine.board import Board
from engine.algorithms import alphabeta_mo
from engine.data_structures import Node, toUCI

Search = namedtuple(
    "Search", ["move", "depth", "score", "nodes", "time", "best_node", "pv"]
)

def search(board: Board, depth: int, eval_guess: int = 0):

    start_time = time.process_time_ns()

    best = Node(
        depth=depth,
        value=(VALUE_MAX if board.turn == COLOR.BLACK else -VALUE_MAX),
    )
    nodes = 0

    for move in board.moves():
        curr_board = board.copy()
        curr_board.push(move)
        # node = aspiration_window(curr_board, eval_guess, depth, deque([move]))
        # node = negaC(curr_board, -VALUE_MAX, VALUE_MAX, depth)
        # node = alphabeta_tt_mo(curr_board, -VALUE_MAX, VALUE_MAX, depth, deque([move]))
        # node = alphabeta_tt(curr_board, -VALUE_MAX, VALUE_MAX, depth, deque([move]))
        # node = alphabeta(curr_board, -VALUE_MAX, VALUE_MAX, depth, deque([move]))
        # node = minimax_tt(curr_board, depth, deque([move]))
        # node = minimax(curr_board, depth, deque([move]))
        node = alphabeta_mo(curr_board, -VALUE_MAX, VALUE_MAX, depth, deque([move]))
        nodes += node.children + 1

        if board.turn == COLOR.WHITE:
            if node.value >= best.value:
                best = Node(
                    depth=depth,
                    value=node.value,
                    pv=node.pv,
                    type=node.type,
                    lower=node.lower,
                    upper=node.upper,
                )
        else:
            if node.value <= best.value:
                best = Node(
                    depth=depth,
                    value=node.value,
                    pv=node.pv,
                    type=node.type,
                    lower=node.lower,
                    upper=node.upper,
                )

    return Search(
        move=best.pv[0],
        pv=best.pv,
        depth=depth,
        nodes=nodes,
        score=best.value,
        time=(time.process_time_ns() - start_time),
        best_node=best,
    )


# not validated
def aspiration_window(board: Board, guess: int, depth: int, pv: deque) -> Node:
    lower = guess - 50
    upper = guess + 50
    iteration = 0
    while True:
        iteration += 1
        # node = negaC(board, lower, upper, depth)
        node = alphabeta(board, lower, upper, depth, pv)
        if node.value > upper:
            upper += 100 * (iteration**2)
            continue
        if node.value < lower:
            lower -= 100 * (iteration**2)
            continue
        break
    return node


# In my tests, negaC was slower than just using an aspiration window
# def negaC(board, min: int, max: int, depth: int) -> Node:
#    while min < max - 1:
#        alpha = (min + max + 1) // 2
#        node = alphabeta(board, alpha, alpha + 100, depth)
#        if node.value > alpha:
#            min = node.value
#        else:
#            max = node.value
#    return node
