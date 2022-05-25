import sys
import random
import chess

def eval(board):
    """Naive board evaluation"""
    value = 0
    value = value + len(board.pieces(chess.PAWN, chess.WHITE)) * 10
    value = value + len(board.pieces(chess.KNIGHT, chess.WHITE)) * 30
    value = value + len(board.pieces(chess.BISHOP, chess.WHITE)) * 30
    value = value + len(board.pieces(chess.ROOK, chess.WHITE)) * 50
    value = value + len(board.pieces(chess.QUEEN, chess.WHITE)) * 90
    value = value - len(board.pieces(chess.PAWN, chess.BLACK)) * 10
    value = value - len(board.pieces(chess.KNIGHT, chess.BLACK)) * 30
    value = value - len(board.pieces(chess.BISHOP, chess.BLACK)) * 30
    value = value - len(board.pieces(chess.ROOK, chess.BLACK)) * 50
    value = value - len(board.pieces(chess.QUEEN, chess.BLACK)) * 90
    #value += random.randrange(0, 10)
    if board.turn == chess.BLACK:
        value *= -1
    return value


def search_best_move(board, depth):
    """Naive best move search"""
    best_move = None
    best_value = -10000
    #print(board)
    #print([x.uci() for x in board.legal_moves])
    for move in board.legal_moves:
        #print("---")
        curr_board = board.copy()
        curr_board.push(move)
        t = alphaBeta(curr_board, -10000, 10000, depth)
        value = -t[0]
        ml = t[1]
        #print("{}: {} {}".format(move.uci(), value, ",".join([x.uci() for x in ml])))
        if value > best_value:
            best_move = move
            best_value = value
    #print("-------------------------------")
    return best_move


def alphaBeta(board, alpha, beta, depthleft) -> set:
    if board.is_game_over():
        outcome = board.outcome()
        if outcome.winner is None:
            return (0, [])
        if outcome.winner == board.turn:
            return (-1000, [])
        return (1000, [])
    if depthleft == 0:
        return (-eval(board), [])
    value = -1000
    move_list = []
    #if (depthleft == 3):
    #    print(board)
    #    print("to evaluate: {}".format([x.uci() for x in board.legal_moves]))
    for move in board.legal_moves:
        #if (depthleft == 3):
        #    print("evaluating: {}".format(move.uci()))
        curr_board = chess.Board(board.fen())
        curr_board.push(move)
        t = alphaBeta(curr_board, -beta, -alpha, depthleft - 1)
        ab = t[0]
        ml = [move, *t[1]]
        #if (depthleft == 3):
        #    print((depthleft, ab, ml))
        if value < ab:
            value = ab
            move_list = ml
        alpha = max(alpha, value)
        if alpha >= beta:
            #if (depthleft == 3):
            #    print("BREAK: {}, {}, {}, {}".format(move_list, alpha, beta, value))
            break
    return (value, move_list)


def bestMove(fen, depth):
    board = chess.Board(fen)
    best_move = search_best_move(board, depth)
    return best_move.uci()


# rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
if __name__ == "__main__":
    depth = int(sys.argv[1])
    if sys.argv[2] == "startpos":
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    else:
        fen = " ".join(sys.argv[2:])
    print("{}".format(best_move.uci()))
