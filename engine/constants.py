import enum

class VALUE(enum.IntEnum):
    PAWN = 100
    KNIGHT = 300
    BISHOP = 300
    ROOK = 500
    QUEEN = 1000
    KING = 10000
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

class SQUARE(enum.IntEnum):
    A1 = 0
    B1 = 1
    C1 = 2
    D1 = 3
    E1 = 4
    F1 = 5
    G1 = 6
    H1 = 7
    A2 = 8
    B2 = 9
    C2 = 10
    D2 = 11
    E2 = 12
    F2 = 13
    G2 = 14
    H2 = 15
    A3 = 16
    B3 = 17
    C3 = 18
    D3 = 19
    E3 = 20
    F3 = 21
    G3 = 22
    H3 = 23
    A4 = 24
    B4 = 25
    C4 = 26
    D4 = 27
    E4 = 28
    F4 = 29
    G4 = 30
    H4 = 31
    A5 = 32
    B5 = 33
    C5 = 34
    D5 = 35
    E5 = 36
    F5 = 37
    G5 = 38
    H5 = 39
    A6 = 40
    B6 = 41
    C6 = 42
    D6 = 43
    E6 = 44
    F6 = 45
    G6 = 46
    H6 = 47
    A7 = 48
    B7 = 49
    C7 = 50
    D7 = 51
    E7 = 52
    F7 = 53
    G7 = 54
    H7 = 55
    A8 = 56
    B8 = 57
    C8 = 58
    D8 = 59
    E8 = 60
    F8 = 61
    G8 = 62
    H8 = 63
