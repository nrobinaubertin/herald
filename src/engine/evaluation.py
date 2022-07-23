from array import array
from .constants import PIECE, COLOR

PIECE_VALUE = {
    PIECE.EMPTY: 0,
    PIECE.PAWN: 100,
    PIECE.KNIGHT: 280,
    PIECE.BISHOP: 320,
    PIECE.ROOK: 479,
    PIECE.QUEEN: 929,
    PIECE.KING: 60_000,
}

VALUE_MAX = PIECE_VALUE[PIECE.KING] * 2

DOUBLED_PAWN_PENALTY = -20

# adjustements of piece value based on the number of own pawns
PIECE_ADJUSTEMENTS_OWN_PAWN_NUMBER = {
    PIECE.EMPTY: (0, 0, 0, 0, 0, 0, 0, 0, 0),
    PIECE.PAWN: (0, 0, 0, 0, 0, 0, 0, 0, 0),
    PIECE.KNIGHT: (-20, -16, -12, -8, -4, 0, 4, 8, 12),
    PIECE.BISHOP: (0, 0, 0, 0, 0, 0, 0, 0, 0),
    PIECE.ROOK: (15, 12, 9, 6, 3, 0, -3, -6, -9),
    PIECE.QUEEN: (0, 0, 0, 0, 0, 0, 0, 0, 0),
    PIECE.KING: (0, 0, 0, 0, 0, 0, 0, 0, 0),
}

PIECE_SQUARE_TABLE = {
    PIECE.PAWN: (
        0, 0, 0, 0, 0, 0, 0, 0,
        78, 83, 86, 73, 102, 82, 85, 90,
        7, 29, 21, 44, 40, 31, 44, 7,
        -17, 16, -2, 15, 14, 0, 15, -13,
        -26, 3, 10, 9, 6, 1, 0, -23,
        -22, 9, 5, -11, -10, -2, 3, -19,
        -31, 8, -7, -37, -36, -14, 3, -31,
        0, 0, 0, 0, 0, 0, 0, 0,
    ),
    PIECE.KNIGHT: (
        -66, -53, -75, -75, -10, -55, -58, -70,
        -3, -6, 100, -36, 4, 62, -4, -14,
        10, 67, 1, 74, 73, 27, 62, -2,
        24, 24, 45, 37, 33, 41, 25, 17,
        -1, 5, 31, 21, 22, 35, 2, 0,
        -18, 10, 13, 22, 18, 15, 11, -14,
        -23, -15, 2, 0, 2, 0, -23, -20,
        -74, -23, -26, -24, -19, -35, -22, -69,
    ),
    PIECE.BISHOP: (
        -59, -78, -82, -76, -23, -107, -37, -50,
        -11, 20, 35, -42, -39, 31, 2, -22,
        -9, 39, -32, 41, 52, -10, 28, -14,
        25, 17, 20, 34, 26, 25, 15, 10,
        13, 10, 17, 23, 17, 16, 0, 7,
        14, 25, 24, 15, 8, 25, 20, 15,
        19, 20, 11, 6, 7, 6, 20, 16,
        -7, 2, -15, -12, -14, -15, -10, -10,
    ),
    PIECE.ROOK: (
        35, 29, 33, 4, 37, 33, 56, 50,
        55, 29, 56, 67, 55, 62, 34, 60,
        19, 35, 28, 33, 45, 27, 25, 15,
        0, 5, 16, 13, 18, -4, -9, -6,
        -28, -35, -16, -21, -13, -29, -46, -30,
        -42, -28, -42, -25, -25, -35, -26, -46,
        -53, -38, -31, -26, -29, -43, -44, -53,
        -30, -24, -18, 5, -2, -18, -31, -32,
    ),
    PIECE.QUEEN: (
        6, 1, -8, -104, 69, 24, 88, 26,
        14, 32, 60, -10, 20, 76, 57, 24,
        -2, 43, 32, 60, 72, 63, 43, 2,
        1, -16, 22, 17, 25, 20, -13, -6,
        -14, -15, -2, -5, -1, -10, -20, -22,
        -30, -6, -13, -11, -16, -11, -16, -27,
        -36, -18, 0, -19, -15, -15, -21, -38,
        -39, -30, -31, -13, -31, -36, -34, -42,
    ),
    PIECE.KING: (
        4, 54, 47, -99, -99, 60, 83, -62,
        -32, 10, 55, 56, 56, 55, 10, 3,
        -62, 12, -57, 44, -67, 28, 37, -31,
        -55, 50, 11, -4, -19, 13, 0, -49,
        -55, -43, -52, -28, -51, -47, -8, -50,
        -47, -42, -43, -79, -64, -32, -29, -32,
        -4, 3, -14, -50, -57, -18, 13, 4,
        17, 30, -3, -14, 6, -1, 40, 18,
    ),
}

# arrange pst to match our mailbox
PIECE_SQUARE_TABLE_MAILBOX = {
    PIECE.PAWN: None,
    PIECE.KNIGHT: None,
    PIECE.BISHOP: None,
    PIECE.ROOK: None,
    PIECE.QUEEN: None,
    PIECE.KING: None,
}

# Initialize PIECE_SQUARE_TABLE_MAILBOX
for piece in PIECE_SQUARE_TABLE:
    new_table = array("b")
    for i in range(20):
        new_table.append(0)
    for i in range(8):
        new_table.append(0)  # first column of the mailbox
        for j in range(8):
            new_table.append(PIECE_SQUARE_TABLE[piece][i * 8 + j])
        new_table.append(0)  # last column of the mailbox
    for i in range(20):
        new_table.append(0)
    PIECE_SQUARE_TABLE_MAILBOX[piece] = new_table


def simple_eval(board) -> int:
    evaluation = 0
    for piece in board.pieces:
        evaluation += PIECE_VALUE[abs(piece)] * (abs(piece) // piece)
    return evaluation


def eval_pst(board) -> int:
    evaluation = 0
    for piece in board.pieces:
        for square in board.pieces[piece]:
            color = abs(piece) // piece
            evaluation += PIECE_VALUE[abs(piece)] * color
            if color == COLOR.WHITE:
                evaluation += PIECE_SQUARE_TABLE_MAILBOX[abs(piece)][square] * color
            else:
                evaluation += (
                    PIECE_SQUARE_TABLE_MAILBOX[abs(piece)][120 - square] * color
                )
    return evaluation


# simple eval + pst + adjustements
def eval_pst_adj(board) -> int:
    evaluation = 0
    pawn_number = {
        COLOR.WHITE: len(board.pieces[PIECE.PAWN * COLOR.WHITE]),
        COLOR.BLACK: len(board.pieces[PIECE.PAWN * COLOR.BLACK]),
    }
    for piece in board.pieces:
        for square in board.pieces[piece]:
            color = abs(piece) // piece
            evaluation += PIECE_VALUE[abs(piece)] * color
            evaluation += PIECE_ADJUSTEMENTS_OWN_PAWN_NUMBER[abs(piece)][
                pawn_number[color]
            ]
            if color == COLOR.WHITE:
                evaluation += PIECE_SQUARE_TABLE_MAILBOX[abs(piece)][square] * color
            else:
                evaluation += (
                    PIECE_SQUARE_TABLE_MAILBOX[abs(piece)][120 - square] * color
                )
            if abs(piece) == PIECE.PAWN:
                if board.squares[square - 10 * color] == PIECE.PAWN * color:
                    evaluation -= DOUBLED_PAWN_PENALTY * color
    return evaluation


def eval_board(board) -> int:
    return eval_pst_adj(board)
    # return eval_pst(board)
    # return simple_eval(board)


def move_eval(board, move) -> int:
    if move.is_capture:
        return PIECE_VALUE[abs(board.squares[move.end])]
    return 0
