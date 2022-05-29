import time
import board_simple

def perft(fen, depth) -> int:
    start_time = time.process_time()
    board = board_simple.Board(fen)
    nodes = execute(board, depth)
    print(f"duration: {time.process_time() - start_time}")
    return nodes

def execute(board, depth: int) -> int:
    if depth == 1:
        return len([x for x in board.moves()])

    nodes = 0
    for move in board.moves():
        curr_board = board.copy()
        curr_board.push(move)
        nodes += execute(curr_board, depth - 1)

    return nodes
