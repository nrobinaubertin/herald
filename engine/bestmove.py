import sys
import board_simple
import eval_simple
import alphabeta_simple

def bestMove(fen, depth):
    board = board_simple.Board(fen)
    best_move = alphabeta_simple.search_best_move(board, depth, eval_simple.eval)
    return best_move.uci()

if __name__ == "__main__":
    depth = int(sys.argv[1])
    if sys.argv[2] == "startpos":
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    else:
        fen = " ".join(sys.argv[2:])
    print("{}".format(best_move.uci()))
