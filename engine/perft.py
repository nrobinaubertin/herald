"""Perft: performance test"""
import time


def perft(board, depth) -> int:
    """Start the perft"""
    start_time = time.process_time()
    nodes = execute(board, depth)
    print(f"duration: {time.process_time() - start_time}")
    return nodes


def execute(board, depth: int) -> int:
    """recursively called perft function"""
    if depth == 1:
        return len(board.pseudo_legal_moves())

    nodes = 0
    for move in board.pseudo_legal_moves():
        curr_board = board.copy()
        curr_board.push(move)
        nodes += execute(curr_board, depth - 1)

    return nodes


if __name__ == "__main__":
    perft("startpos", 5)
