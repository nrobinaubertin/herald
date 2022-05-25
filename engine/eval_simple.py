import constants

def eval(board) -> int:
    """Naive board evaluation"""
    value = 0
    value += len(board.pieces(constants.PIECE.PAWN, constants.COLOR.WHITE)) * constants.VALUE.PAWN
    value += len(board.pieces(constants.PIECE.KNIGHT, constants.COLOR.WHITE)) * constants.VALUE.KNIGHT
    value += len(board.pieces(constants.PIECE.BISHOP, constants.COLOR.WHITE)) * constants.VALUE.BISHOP
    value += len(board.pieces(constants.PIECE.ROOK, constants.COLOR.WHITE)) * constants.VALUE.ROOK
    value += len(board.pieces(constants.PIECE.QUEEN, constants.COLOR.WHITE)) * constants.VALUE.QUEEN
    value -= len(board.pieces(constants.PIECE.PAWN, constants.COLOR.BLACK)) * constants.VALUE.PAWN
    value -= len(board.pieces(constants.PIECE.KNIGHT, constants.COLOR.BLACK)) * constants.VALUE.KNIGHT
    value -= len(board.pieces(constants.PIECE.BISHOP, constants.COLOR.BLACK)) * constants.VALUE.BISHOP
    value -= len(board.pieces(constants.PIECE.ROOK, constants.COLOR.BLACK)) * constants.VALUE.ROOK
    value -= len(board.pieces(constants.PIECE.QUEEN, constants.COLOR.BLACK)) * constants.VALUE.QUEEN
    if board.turn == constants.COLOR.BLACK:
        value *= -1
    return value
