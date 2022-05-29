import constants

def search_best_move(board, depth: int, eval_fn):
    best_move = None
    best_value = constants.VALUE.MAX * -1
    for move in board.moves():
        curr_board = board.copy()
        curr_board.push(move)
        value = alphaBeta(curr_board, constants.VALUE.MAX * -1, constants.VALUE.MAX, depth, eval_fn)
        #print("{}: {}".format(move.uci(), value))
        if value > best_value:
            best_move = move
            best_value = value
    return best_move


def alphaBeta(board, alpha: int, beta: int, depthleft: int, eval_fn) -> int:
    if board.is_game_over():
        outcome = board.outcome()
        if outcome.winner is None:
            return 0
        if outcome.winner == board.turn:
            return constants.VALUE.MAX * -1
        return constants.VALUE.MAX
    if depthleft == 0:
        return -eval_fn(board)
    value = constants.VALUE.MAX * -1
    for move in board.moves():
        curr_board = board.copy()
        curr_board.push(move)
        value = max(value, alphaBeta(curr_board, -beta, -alpha, depthleft - 1, eval_fn))
        alpha = max(alpha, value)
        if alpha >= beta:
            break
    return value
