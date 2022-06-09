import sys
import time
import board as b
import evaluation
import alphabeta_quiescence

def bestMove(fen, depth):
    board = b.Board(fen)
    best_move = alphabeta_quiescence.search_best_move(board, depth, evaluation.eval)
    return b.toUCI(best_move)

if __name__ == "__main__":
    board = b.Board("6kr/p1nprppp/3p4/1p2p3/4P1qP/1P1B4/PBPP1PPR/RQ4K1 b - - 9 34")
    #board = b.Board("startpos")
    start_time = time.process_time()
    depth = 4
    best_move = alphabeta_quiescence.search_best_move(board, depth, evaluation.eval)
    #for i in range(depth + 1):
    #    best_move = alphabeta_quiescence.search_best_move(board, i, evaluation.eval)
    print()
    print(f"Total Search time: {time.process_time() - start_time}")
    print(f"Initial board eval: {board.eval}")
