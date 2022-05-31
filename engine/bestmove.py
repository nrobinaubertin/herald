import sys
import board as b
import evaluation
import alphabeta_quiescence

def bestMove(fen, depth):
    board = b.Board(fen)
    best_move = alphabeta_quiescence.search_best_move(board, depth, evaluation.eval)
    #print(best_move)
    return b.toUCI(best_move)
