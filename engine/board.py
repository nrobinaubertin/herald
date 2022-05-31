import enum
import collections
import copy
import array
from zlib import adler32

from constants import PIECE, COLOR, ASCII_REP, CASTLE

Move = collections.namedtuple(
    "Move",
    ["start", "end", "is_capture", "is_castle", "en_passant"],
    defaults={
        "start": 0,
        "end": 0,
        "is_capture": False,
        "is_castle": False,
        "en_passant": -1,
    },
)

def toNormalNotation(square: int) -> str:
    row = 10 - (square // 10 - 2)
    column = square - (square // 10) * 10
    letter = ({1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'g', 8: 'h'})[column]
    return f"{letter}{row - 2}"


def toUCI(move: Move) -> str:
    return f"{toNormalNotation(move.start)}{toNormalNotation(move.end)}"

class Board:
    def toString(self) -> str:
        rep = f"{'w' if board.turn == COLOR.WHITE else 'b'}  0 1 2 3 4 5 6 7 8 9"
        for i in range(120):
            if i % 10 == 0:
                rep += f"\n{i//10:02d} "
            if self.squares[i] == PIECE.INVALID:
                rep += "- "
                continue
            rep += f"{ASCII_REP[self.squares[i]]} "
        return rep

    def __str__(self) -> str:
        return self.toString()

    def init(self):
        # list of PIECE * COLOR
        # 120 squares for a 10*12 mailbox (https://www.chessprogramming.org/Mailbox)
        self.squares = [PIECE.INVALID] * 120

        # dict of PIECE * COLOR => set(squares)
        self.pieces = {
            (PIECE.PAWN * COLOR.WHITE): set(),
            (PIECE.KNIGHT * COLOR.WHITE): set(),
            (PIECE.BISHOP * COLOR.WHITE): set(),
            (PIECE.ROOK * COLOR.WHITE): set(),
            (PIECE.QUEEN * COLOR.WHITE): set(),
            (PIECE.KING * COLOR.WHITE): set(),
            (PIECE.PAWN * COLOR.BLACK): set(),
            (PIECE.KNIGHT * COLOR.BLACK): set(),
            (PIECE.BISHOP * COLOR.BLACK): set(),
            (PIECE.ROOK * COLOR.BLACK): set(),
            (PIECE.QUEEN * COLOR.BLACK): set(),
            (PIECE.KING * COLOR.BLACK): set(),
        }

        self.turn = COLOR.WHITE
        self.castling_rights = set()
        self.en_passant = -1
        self.half_move = 0
        self.full_move = 0

    def hash(self):
        data = array.array('b')
        data.fromlist(self.squares[20:99])
        data.append(self.turn)
        for cr in self.castling_rights:
            data.append(cr)
        data.append(self.en_passant)
        #data.append(self.half_move)
        return adler32(data)

    def from_FEN(self, fen: str):
        if fen == "startpos":
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        board, turn, castling_rights, en_passant, half_move, full_move = fen.split()

        self.init()
        self.turn = COLOR.WHITE if turn == "w" else COLOR.BLACK
        if "K" in castling_rights:
            self.castling_rights.add(CASTLE.KING_SIDE * COLOR.WHITE)
        if "Q" in castling_rights:
            self.castling_rights.add(CASTLE.QUEEN_SIDE * COLOR.WHITE)
        if "k" in castling_rights:
            self.castling_rights.add(CASTLE.KING_SIDE * COLOR.BLACK)
        if "q" in castling_rights:
            self.castling_rights.add(CASTLE.QUEEN_SIDE * COLOR.BLACK)
        self.en_passant = -1 # TODO
        self.half_move = int(half_move)
        self.full_move = int(full_move)

        s = 19
        for row in board.split("/"):
            self.squares[s := s + 1] = PIECE.INVALID
            for c in row:
                if c.lower() == "r":
                    piece = PIECE.ROOK * (COLOR.BLACK if c.islower() else COLOR.WHITE)
                    self.squares[s := s + 1] = piece
                    self.pieces[piece].add(s)
                    continue
                if c.lower() == "n":
                    piece = PIECE.KNIGHT * (COLOR.BLACK if c.islower() else COLOR.WHITE)
                    self.squares[s := s + 1] = piece
                    self.pieces[piece].add(s)
                    continue
                if c.lower() == "b":
                    piece = PIECE.BISHOP * (COLOR.BLACK if c.islower() else COLOR.WHITE)
                    self.squares[s := s + 1] = piece
                    self.pieces[piece].add(s)
                    continue
                if c.lower() == "q":
                    piece = PIECE.QUEEN * (COLOR.BLACK if c.islower() else COLOR.WHITE)
                    self.squares[s := s + 1] = piece
                    self.pieces[piece].add(s)
                    continue
                if c.lower() == "k":
                    piece = PIECE.KING * (COLOR.BLACK if c.islower() else COLOR.WHITE)
                    self.squares[s := s + 1] = piece
                    self.pieces[piece].add(s)
                    continue
                if c.lower() == "p":
                    piece = PIECE.PAWN * (COLOR.BLACK if c.islower() else COLOR.WHITE)
                    self.squares[s := s + 1] = piece
                    self.pieces[piece].add(s)
                    continue
                if int(c) > 0:
                    for i in range(int(c)):
                        self.squares[s := s + 1] = PIECE.EMPTY
            self.squares[s := s + 1] = PIECE.INVALID

    def __init__(self, fen=""):
        if fen:
            self.from_FEN(fen)
        else:
            self.init()

    def push(self, move: Move):

        piece_start = self.squares[move.start]
        piece_end = self.squares[move.end]
        self.squares[move.start] = PIECE.EMPTY
        self.squares[move.end] = piece_start
        self.pieces[piece_start].remove(move.start)
        self.pieces[piece_start].add(move.end)
        if piece_end != PIECE.EMPTY:
            self.pieces[piece_end].remove(move.end)

        # special removal for "en passant" moves
        if (
            piece_start == PIECE.PAWN * self.turn
            and move.is_capture
            and piece_end == PIECE.EMPTY
            and move.end == self.en_passant
        ):
            target = move.end + (10 * self.turn)
            target_piece = self.squares[target]
            self.squares[target] = PIECE.EMPTY
            self.pieces[target_piece].remove(target)

        if move.en_passant != -1:
            self.en_passant = move.en_passant
        else:
            self.en_passant = -1

        # some hardcode for castling move of the rook
        if move.is_castle:
            if move.end == 97:
                self.squares[98] = PIECE.EMPTY
                self.squares[96] = PIECE.ROOK * COLOR.WHITE
                self.pieces[PIECE.ROOK * COLOR.WHITE].remove(98)
                self.pieces[PIECE.ROOK * COLOR.WHITE].add(96)
            if move.end == 93:
                self.squares[91] = PIECE.EMPTY
                self.squares[95] = PIECE.ROOK * COLOR.WHITE
                self.pieces[PIECE.ROOK * COLOR.WHITE].remove(91)
                self.pieces[PIECE.ROOK * COLOR.WHITE].add(94)
            if move.end == 27:
                self.squares[28] = PIECE.EMPTY
                self.squares[26] = PIECE.ROOK * COLOR.BLACK
                self.pieces[PIECE.ROOK * COLOR.BLACK].remove(28)
                self.pieces[PIECE.ROOK * COLOR.BLACK].add(26)
            if move.end == 23:
                self.squares[21] = PIECE.EMPTY
                self.squares[24] = PIECE.ROOK * COLOR.BLACK
                self.pieces[PIECE.ROOK * COLOR.BLACK].remove(21)
                self.pieces[PIECE.ROOK * COLOR.BLACK].add(24)

        # remove castling rights
        if (
            move.end == 98
            or move.start == 98
            or piece_start == PIECE.KING * COLOR.WHITE
        ):
            self.castling_rights.discard(CASTLE.KING_SIDE * COLOR.WHITE)
        if (
            move.end == 91
            or move.start == 91
            or piece_start == PIECE.KING * COLOR.WHITE
        ):
            self.castling_rights.discard(CASTLE.QUEEN_SIDE * COLOR.WHITE)
        if (
            move.end == 28
            or move.start == 28
            or piece_start == PIECE.KING * COLOR.BLACK
        ):
            self.castling_rights.discard(CASTLE.KING_SIDE * COLOR.BLACK)
        if (
            move.end == 21
            or move.start == 21
            or piece_start == PIECE.KING * COLOR.BLACK
        ):
            self.castling_rights.discard(CASTLE.QUEEN_SIDE * COLOR.BLACK)

        self.turn = COLOR.BLACK if self.turn == COLOR.WHITE else COLOR.WHITE
        self.half_move += 1
        self.full_move += 1

    def copy(self):
        board = Board()
        board.init()
        board.squares = copy.deepcopy(self.squares)
        board.pieces = copy.deepcopy(self.pieces)
        board.turn = self.turn
        board.castling_rights = self.castling_rights
        board.en_passant = self.en_passant
        board.half_move = self.half_move
        board.full_move = self.full_move
        return board

    def moves(self):
        moves = []
        for move in self.pseudo_legal_moves():
            b = self.copy()
            b.push(move)
            if not b.is_square_attacked(
                next(
                    iter(
                        b.pieces[
                            PIECE.KING
                            * (COLOR.WHITE if b.turn == COLOR.BLACK else COLOR.BLACK)
                        ]
                    )
                ),
                b.turn,
            ):
                moves.append(move)
        return moves

    def is_square_attacked(self, square: int, color: COLOR) -> bool:
        for depl in [21, 12, -8, -19, -21, -12, 8, 19]:
            if self.squares[square + depl] == PIECE.KNIGHT * color:
                return True
        for direction in [1, -1, 10, -10]:
            for depl in [x * direction for x in range(1, 7)]:
                end = square + depl
                if self.squares[end] == PIECE.ROOK * color:
                    return True
                if self.squares[end] != PIECE.EMPTY:
                    break
        for direction in [11, -11, 9, -9]:
            for depl in [x * direction for x in range(1, 7)]:
                end = square + depl
                if self.squares[end] == PIECE.BISHOP * color:
                    return True
                if self.squares[end] != PIECE.EMPTY:
                    break
        for direction in [11, -11, 9, -9] + [1, -1, 10, -10]:
            for depl in [x * direction for x in range(1, 7)]:
                end = square + depl
                if self.squares[end] == PIECE.QUEEN * color:
                    return True
                if self.squares[end] != PIECE.EMPTY:
                    break
        for depl in [11, -11, 9, -9] + [1, -1, 10, -10]:
            if self.squares[square + depl] == PIECE.KING * color:
                return True
        for depl in [9, 11] if color == COLOR.WHITE else [-9, -11]:
            if self.squares[square + depl] == PIECE.PAWN * color:
                return True
        return False

    def pseudo_legal_moves(self):
        moves = []
        for type in [
            PIECE.PAWN,
            PIECE.KNIGHT,
            PIECE.BISHOP,
            PIECE.ROOK,
            PIECE.QUEEN,
            PIECE.KING,
        ]:
            for start in self.pieces[type * self.turn]:
                if type == PIECE.KNIGHT:
                    for depl in [21, 12, -8, -19, -21, -12, 8, 19]:
                        end = start + depl
                        if (
                            self.squares[end] != PIECE.INVALID
                            and self.squares[end] * self.turn <= 0
                        ):
                            moves.append(
                                Move(
                                    start=start,
                                    end=end,
                                    is_capture=(bool(self.squares[start])),
                                    is_castle=False,
                                    en_passant=-1,
                                )
                            )
                if type == PIECE.ROOK:
                    for direction in [1, -1, 10, -10]:
                        for depl in [x * direction for x in range(1, 7)]:
                            end = start + depl
                            if (
                                self.squares[end] != PIECE.INVALID
                                and self.squares[end] * self.turn <= 0
                            ):
                                moves.append(
                                    Move(
                                        start=start,
                                        end=end,
                                        is_capture=(bool(self.squares[start])),
                                        is_castle=False,
                                        en_passant=-1,
                                    )
                                )
                            if self.squares[end] != PIECE.EMPTY:
                                break
                if type == PIECE.BISHOP:
                    for direction in [11, -11, 9, -9]:
                        for depl in [x * direction for x in range(1, 7)]:
                            end = start + depl
                            if (
                                self.squares[end] != PIECE.INVALID
                                and self.squares[end] * self.turn <= 0
                            ):
                                moves.append(
                                    Move(
                                        start=start,
                                        end=end,
                                        is_capture=(bool(self.squares[start])),
                                        is_castle=False,
                                        en_passant=-1,
                                    )
                                )
                            if self.squares[end] != PIECE.EMPTY:
                                break
                if type == PIECE.QUEEN:
                    for direction in [11, -11, 9, -9] + [1, -1, 10, -10]:
                        for depl in [x * direction for x in range(1, 7)]:
                            end = start + depl
                            if (
                                self.squares[end] != PIECE.INVALID
                                and self.squares[end] * self.turn <= 0
                            ):
                                moves.append(
                                    Move(
                                        start=start,
                                        end=end,
                                        is_capture=(bool(self.squares[start])),
                                        is_castle=False,
                                        en_passant=-1,
                                    )
                                )
                            if self.squares[end] != PIECE.EMPTY:
                                break
                if type == PIECE.KING:
                    for depl in [11, -11, 9, -9] + [1, -1, 10, -10]:
                        end = start + depl
                        if (
                            self.squares[end] != PIECE.INVALID
                            and self.squares[end] * self.turn <= 0
                        ):
                            moves.append(
                                Move(
                                    start=start,
                                    end=end,
                                    is_capture=(bool(self.squares[start])),
                                    is_castle=False,
                                    en_passant=-1,
                                )
                            )
                if type == PIECE.PAWN:
                    depls = [(10 if self.turn == COLOR.BLACK else -10)]
                    if start // 10 == (3 if self.turn == COLOR.BLACK else 8):
                        depls.append((20 if self.turn == COLOR.BLACK else -20))
                    for idx, depl in enumerate(depls):
                        end = start + depl
                        if self.squares[end] == PIECE.EMPTY:
                            if idx == 1:
                                en_passant = start + depls[0]
                            else:
                                en_passant = -1
                            moves.append(
                                Move(
                                    start=start,
                                    end=end,
                                    is_capture=(bool(self.squares[start])),
                                    is_castle=False,
                                    en_passant=en_passant,
                                )
                            )
                        else:
                            # do not allow 2 squares move if there's a piece in the way
                            break
                    for depl in [9, 11] if self.turn == COLOR.BLACK else [-9, -11]:
                        end = start + depl
                        if (
                            self.squares[end] != PIECE.INVALID
                            and self.squares[end] * self.turn < 0
                        ) or end == self.en_passant:
                            moves.append(
                                Move(
                                    start=start,
                                    end=end,
                                    is_capture=(
                                        end == self.en_passant
                                        or bool(self.squares[start])
                                    ),
                                    is_castle=False,
                                    en_passant=-1,
                                )
                            )
        # castling moves
        for castle in self.castling_rights:
            if castle > 0 and self.turn == COLOR.WHITE:
                if (
                    abs(castle) == CASTLE.KING_SIDE
                    and self.squares[96] == PIECE.EMPTY
                    and not self.is_square_attacked(95, COLOR.BLACK)
                    and not self.is_square_attacked(96, COLOR.BLACK)
                    and not self.is_square_attacked(97, COLOR.BLACK)
                ):
                    moves.append(
                        Move(
                            start=95,
                            end=97,
                            is_capture=False,
                            is_castle=True,
                            en_passant=-1,
                        )
                    )
                if (
                    abs(castle) == CASTLE.QUEEN_SIDE
                    and self.squares[94] == PIECE.EMPTY
                    and not self.is_square_attacked(95, COLOR.BLACK)
                    and not self.is_square_attacked(94, COLOR.BLACK)
                    and not self.is_square_attacked(93, COLOR.BLACK)
                ):
                    moves.append(
                        Move(
                            start=95,
                            end=93,
                            is_capture=False,
                            is_castle=True,
                            en_passant=-1,
                        )
                    )
            if castle < 0 and self.turn == COLOR.BLACK:
                if (
                    abs(castle) == CASTLE.KING_SIDE
                    and self.squares[26] == PIECE.EMPTY
                    and not self.is_square_attacked(25, COLOR.WHITE)
                    and not self.is_square_attacked(26, COLOR.WHITE)
                    and not self.is_square_attacked(27, COLOR.WHITE)
                ):
                    moves.append(
                        Move(
                            start=25,
                            end=27,
                            is_capture=False,
                            is_castle=True,
                            en_passant=-1,
                        )
                    )
                if (
                    abs(castle) == CASTLE.QUEEN_SIDE
                    and self.squares[24] == PIECE.EMPTY
                    and not self.is_square_attacked(25, COLOR.WHITE)
                    and not self.is_square_attacked(24, COLOR.WHITE)
                    and not self.is_square_attacked(23, COLOR.WHITE)
                ):
                    moves.append(
                        Move(
                            start=25,
                            end=23,
                            is_capture=False,
                            is_castle=True,
                            en_passant=-1,
                        )
                    )
        return moves
