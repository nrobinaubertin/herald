import enum

class VALUE(enum.IntEnum):
    PAWN = 100
    KNIGHT = 300
    BISHOP = 300
    ROOK = 500
    QUEEN = 1000
    MAX = 100000

class COLOR(enum.IntEnum):
    WHITE = 1
    BLACK = -1

class PIECE(enum.IntEnum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6

STARTPOS = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
