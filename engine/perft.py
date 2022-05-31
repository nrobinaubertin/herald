import time
import board as b


def perft(fen, depth) -> int:
    start_time = time.process_time()
    board = b.Board(fen)
    nodes = execute(board, depth)
    print(f"duration: {time.process_time() - start_time}")
    return nodes


def execute(board, depth: int) -> int:
    if depth == 1:
        return len([x for x in board.moves()])

    nodes = 0
    moves = board.moves()
    for move in moves:
        curr_board = board.copy()
        curr_board.push(move)
        nodes += execute(curr_board, depth - 1)

    return nodes
