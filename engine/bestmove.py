import sys
import board as b
import evaluation
import alphabeta_quiescence

def bestMove(fen, depth):
    board = b.Board(fen)
    best_move = alphabeta_quiescence.search_best_move(board, depth, evaluation.eval)
    #print(best_move)
    return b.toUCI(best_move)

if __name__ == "__main__":
    board = b.Board("r1bqkb1r/pppppppp/5n2/8/1n1PP3/P1N5/1PP2PPP/R1BQKBNR b KQkq - 0 4")
    print(alphabeta_quiescence.search_best_move(board, 3, evaluation.eval))
