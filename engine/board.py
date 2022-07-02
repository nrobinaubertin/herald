import enum
import collections
import copy
from array import array
from zlib import adler32, crc32
import hashlib
import evaluation

# TO TEST:
# position r1bk3r/pp1n3p/5Q2/1Np5/5pB1/8/PPP2P1P/2KR3R b - - 0 17
# position 2b1k2r/1pp2pp1/5r2/p1b1n3/P1P5/1P3N2/1q1PPPPP/3RKB1R w Kk - 4 21
# position 5r1k/pp6/2p1bn1P/6r1/3pB3/3P4/1PP2R2/2K2R2 b - - 1 33

from constants import PIECE, COLOR, ASCII_REP, CASTLE

Move = collections.namedtuple(
    "Move",
    ["start", "end", "is_capture", "is_castle", "en_passant"],
    defaults=[0, 0, False, False, -1],
)


def toUCI(move: Move) -> str:
    def toNormalNotation(square: int) -> str:
        row = 10 - (square // 10 - 2)
        column = square - (square // 10) * 10
        letter = ({1: "a", 2: "b", 3: "c", 4: "d", 5: "e", 6: "f", 7: "g", 8: "h"})[
            column
        ]
        return f"{letter}{row - 2}"

    return f"{toNormalNotation(move.start)}{toNormalNotation(move.end)}"


class Board:
    def fromUCI(self, uci: str) -> Move:
        digits = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}
        start = digits[uci[0]] + (10 - int(uci[1])) * 10
        end = digits[uci[2]] + (10 - int(uci[3])) * 10
        return Move(
            start=start,
            end=end,
            is_capture=(
                abs(self.squares[end]) != PIECE.EMPTY
                or end == self.en_passant
                or end == self.king_en_passant
            ),
            is_castle=(start == 95 or start == 25) and abs(self.squares[start]) == PIECE.KING and abs(end - start) == 2,
            en_passant=(start + end) // 2 if abs(self.squares[start]) == PIECE.PAWN and abs(start - end) == 20 else -1
        )

    def toString(self) -> str:
        rep = f"{'w' if self.turn == COLOR.WHITE else 'b'}  0 1 2 3 4 5 6 7 8 9"
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
        # array of PIECE * COLOR
        # 120 squares for a 10*12 mailbox (https://www.chessprogramming.org/Mailbox)
        self.squares = array("b", [PIECE.INVALID] * 120)  # [PIECE.INVALID] * 120

        # dict of PIECE * COLOR => set(squares)
        self.pieces = {
            (PIECE.PAWN * COLOR.WHITE): array("b"),
            (PIECE.KNIGHT * COLOR.WHITE): array("b"),
            (PIECE.BISHOP * COLOR.WHITE): array("b"),
            (PIECE.ROOK * COLOR.WHITE): array("b"),
            (PIECE.QUEEN * COLOR.WHITE): array("b"),
            (PIECE.KING * COLOR.WHITE): array("b"),
            (PIECE.PAWN * COLOR.BLACK): array("b"),
            (PIECE.KNIGHT * COLOR.BLACK): array("b"),
            (PIECE.BISHOP * COLOR.BLACK): array("b"),
            (PIECE.ROOK * COLOR.BLACK): array("b"),
            (PIECE.QUEEN * COLOR.BLACK): array("b"),
            (PIECE.KING * COLOR.BLACK): array("b"),
        }

        # array of pieces type per color
        # length 120 to account for max 10 of each type
        # start index for each piece: (color + 1) / 2 * type
        self.pieces_array = array("b", [PIECE.EMPTY] * 120)

        # move history
        self.moves_history = collections.deque()

        self.turn = COLOR.WHITE
        self.castling_rights = array("b")
        self.en_passant = -1
        self.half_move = 0
        self.full_move = 0
        self.king_en_passant = -1
        self.eval = 0

    # def get_pieces_squares(type: PIECE, color: COLOR):
    #    return self.pieces_array[(color + 1) / 2 * type]

    def hash(self):
        data = array("b")
        data.extend(self.squares)
        data.append(self.turn)
        data.extend(self.castling_rights)
        data.append(self.en_passant)
        data.append(self.king_en_passant)
        #return data.tobytes()
        # return data
        return hashlib.sha256(data).hexdigest()
        #return adler32(data)

    def fromFEN(self, fen: str):
        if fen == "startpos":
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        board, turn, castling_rights, en_passant, half_move, full_move = fen.split()

        self.init()
        self.turn = COLOR.WHITE if turn == "w" else COLOR.BLACK
        if "K" in castling_rights:
            self.castling_rights.append(CASTLE.KING_SIDE * COLOR.WHITE)
        if "Q" in castling_rights:
            self.castling_rights.append(CASTLE.QUEEN_SIDE * COLOR.WHITE)
        if "k" in castling_rights:
            self.castling_rights.append(CASTLE.KING_SIDE * COLOR.BLACK)
        if "q" in castling_rights:
            self.castling_rights.append(CASTLE.QUEEN_SIDE * COLOR.BLACK)
        self.en_passant = -1  # TODO
        self.half_move = int(half_move)
        self.full_move = int(full_move)

        s = 19
        for row in board.split("/"):
            self.squares[s := s + 1] = PIECE.INVALID
            for c in row:
                if c.lower() == "r":
                    piece = PIECE.ROOK * (COLOR.BLACK if c.islower() else COLOR.WHITE)
                    self.squares[s := s + 1] = piece
                    self.pieces[piece].append(s)
                    continue
                if c.lower() == "n":
                    piece = PIECE.KNIGHT * (COLOR.BLACK if c.islower() else COLOR.WHITE)
                    self.squares[s := s + 1] = piece
                    self.pieces[piece].append(s)
                    continue
                if c.lower() == "b":
                    piece = PIECE.BISHOP * (COLOR.BLACK if c.islower() else COLOR.WHITE)
                    self.squares[s := s + 1] = piece
                    self.pieces[piece].append(s)
                    continue
                if c.lower() == "q":
                    piece = PIECE.QUEEN * (COLOR.BLACK if c.islower() else COLOR.WHITE)
                    self.squares[s := s + 1] = piece
                    self.pieces[piece].append(s)
                    continue
                if c.lower() == "k":
                    piece = PIECE.KING * (COLOR.BLACK if c.islower() else COLOR.WHITE)
                    self.squares[s := s + 1] = piece
                    self.pieces[piece].append(s)
                    continue
                if c.lower() == "p":
                    piece = PIECE.PAWN * (COLOR.BLACK if c.islower() else COLOR.WHITE)
                    self.squares[s := s + 1] = piece
                    self.pieces[piece].append(s)
                    continue
                if int(c) > 0:
                    for i in range(int(c)):
                        self.squares[s := s + 1] = PIECE.EMPTY
            self.squares[s := s + 1] = PIECE.INVALID
        self.eval = evaluation.eval_board(self)

    def __init__(self, fen=""):
        if fen:
            self.fromFEN(fen)

    def push(self, move: Move):

        piece_start = self.squares[move.start]
        piece_end = self.squares[move.end]

        self.squares[move.start] = PIECE.EMPTY
        self.squares[move.end] = piece_start
        self.pieces[piece_start].remove(move.start)
        self.pieces[piece_start].append(move.end)
        if piece_end != PIECE.EMPTY:
            self.pieces[piece_end].remove(move.end)

        # special removal for "en passant" moves
        if abs(piece_start) == PIECE.PAWN and move.end == self.en_passant:
            target = move.end + (10 * self.turn)
            target_piece = self.squares[target]
            self.squares[target] = PIECE.EMPTY
            self.pieces[target_piece].remove(target)

        # declare en_passant square for the current board
        if move.en_passant != -1:
            self.en_passant = move.en_passant
        else:
            self.en_passant = -1

        # check if the piece ends up on the king_en_passant square
        if move.end == self.king_en_passant:
            king_square = self.pieces[PIECE.KING * self.invturn]
            self.pieces[PIECE.KING * self.invturn] = array("b")
            self.squares[king_square] = PIECE.EMPTY

        # promotion
        if abs(piece_start) == PIECE.PAWN and move.end // 10 == (2 if self.turn == COLOR.WHITE else 9):
            self.squares[move.end] = PIECE.QUEEN * self.turn
            self.pieces[PIECE.PAWN * self.turn].remove(move.end)
            self.pieces[PIECE.QUEEN * self.turn].append(move.end)

        # some hardcode for castling move of the rook
        if move.is_castle:
            if move.end == 97:
                self.squares[98] = PIECE.EMPTY
                self.squares[95] = PIECE.EMPTY
                self.squares[96] = PIECE.ROOK * COLOR.WHITE
                self.pieces[PIECE.ROOK * COLOR.WHITE].remove(98)
                self.pieces[PIECE.ROOK * COLOR.WHITE].append(96)
                self.king_en_passant = 96
            if move.end == 93:
                self.squares[91] = PIECE.EMPTY
                self.squares[95] = PIECE.EMPTY
                self.squares[94] = PIECE.ROOK * COLOR.WHITE
                self.pieces[PIECE.ROOK * COLOR.WHITE].remove(91)
                self.pieces[PIECE.ROOK * COLOR.WHITE].append(94)
                self.king_en_passant = 94
            if move.end == 27:
                self.squares[28] = PIECE.EMPTY
                self.squares[25] = PIECE.EMPTY
                self.squares[26] = PIECE.ROOK * COLOR.BLACK
                self.pieces[PIECE.ROOK * COLOR.BLACK].remove(28)
                self.pieces[PIECE.ROOK * COLOR.BLACK].append(26)
                self.king_en_passant = 26
            if move.end == 23:
                self.squares[21] = PIECE.EMPTY
                self.squares[25] = PIECE.EMPTY
                self.squares[24] = PIECE.ROOK * COLOR.BLACK
                self.pieces[PIECE.ROOK * COLOR.BLACK].remove(21)
                self.pieces[PIECE.ROOK * COLOR.BLACK].append(24)
                self.king_en_passant = 24
        else:
            self.king_en_passant = -1

        try:
            # remove castling rights
            if (
                move.end == 98
                or move.start == 98
                or piece_start == PIECE.KING * COLOR.WHITE
            ):
                self.castling_rights.remove(CASTLE.KING_SIDE * COLOR.WHITE)
            if (
                move.end == 91
                or move.start == 91
                or piece_start == PIECE.KING * COLOR.WHITE
            ):
                self.castling_rights.remove(CASTLE.QUEEN_SIDE * COLOR.WHITE)
            if (
                move.end == 28
                or move.start == 28
                or piece_start == PIECE.KING * COLOR.BLACK
            ):
                self.castling_rights.remove(CASTLE.KING_SIDE * COLOR.BLACK)
            if (
                move.end == 21
                or move.start == 21
                or piece_start == PIECE.KING * COLOR.BLACK
            ):
                self.castling_rights.remove(CASTLE.QUEEN_SIDE * COLOR.BLACK)
        except ValueError:
            pass

        self.moves_history.append(move)
        self.turn = self.invturn
        self.half_move += 1
        self.full_move += 1

    def copy(self):
        board = Board()
        board.squares = array("b", self.squares)
        board.pieces = {
            (PIECE.PAWN * COLOR.WHITE): array(
                "b", self.pieces[PIECE.PAWN * COLOR.WHITE]
            ),
            (PIECE.KNIGHT * COLOR.WHITE): array(
                "b", self.pieces[PIECE.KNIGHT * COLOR.WHITE]
            ),
            (PIECE.BISHOP * COLOR.WHITE): array(
                "b", self.pieces[PIECE.BISHOP * COLOR.WHITE]
            ),
            (PIECE.ROOK * COLOR.WHITE): array(
                "b", self.pieces[PIECE.ROOK * COLOR.WHITE]
            ),
            (PIECE.QUEEN * COLOR.WHITE): array(
                "b", self.pieces[PIECE.QUEEN * COLOR.WHITE]
            ),
            (PIECE.KING * COLOR.WHITE): array(
                "b", self.pieces[PIECE.KING * COLOR.WHITE]
            ),
            (PIECE.PAWN * COLOR.BLACK): array(
                "b", self.pieces[PIECE.PAWN * COLOR.BLACK]
            ),
            (PIECE.KNIGHT * COLOR.BLACK): array(
                "b", self.pieces[PIECE.KNIGHT * COLOR.BLACK]
            ),
            (PIECE.BISHOP * COLOR.BLACK): array(
                "b", self.pieces[PIECE.BISHOP * COLOR.BLACK]
            ),
            (PIECE.ROOK * COLOR.BLACK): array(
                "b", self.pieces[PIECE.ROOK * COLOR.BLACK]
            ),
            (PIECE.QUEEN * COLOR.BLACK): array(
                "b", self.pieces[PIECE.QUEEN * COLOR.BLACK]
            ),
            (PIECE.KING * COLOR.BLACK): array(
                "b", self.pieces[PIECE.KING * COLOR.BLACK]
            ),
        }
        board.moves_history = collections.deque(self.moves_history)
        board.turn = self.turn
        board.castling_rights = self.castling_rights
        board.en_passant = self.en_passant
        board.king_en_passant = self.king_en_passant
        board.half_move = self.half_move
        board.full_move = self.full_move
        board.eval = self.eval
        return board

    @property
    def invturn(self):
        return COLOR.WHITE if self.turn == COLOR.BLACK else COLOR.BLACK

    def moves(self, quiescent=False):
        moves = []
        for move in self.pseudo_legal_moves(quiescent):
            b = self.copy()
            b.push(move)
            if (
                not b.is_square_attacked(
                    b.pieces[PIECE.KING * b.invturn][0],
                    b.turn,
                )
            ) and (
                b.king_en_passant == -1
                or not b.is_square_attacked(b.king_en_passant, b.turn)
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

    def pseudo_legal_moves(self, quiescent=False):
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
                        is_capture = (
                            bool(self.squares[end]) or end == self.king_en_passant
                        )
                        if (
                            self.squares[end] != PIECE.INVALID
                            and self.squares[end] * self.turn <= 0
                            and ((not quiescent) or is_capture)  # quiescence check
                        ):
                            yield Move(
                                start=start,
                                end=end,
                                is_capture=is_capture,
                                is_castle=False,
                                en_passant=-1,
                            )
                if type == PIECE.ROOK:
                    for direction in [1, -1, 10, -10]:
                        for depl in [x * direction for x in range(1, 8)]:
                            end = start + depl
                            is_capture = (
                                bool(self.squares[end]) or end == self.king_en_passant
                            )

                            # castling
                            if not quiescent:
                                for castle in self.castling_rights:
                                    if (
                                        self.turn * castle == CASTLE.KING_SIDE
                                        and start
                                        == (28 if self.turn == COLOR.BLACK else 98)
                                        and self.squares[end] == PIECE.KING * self.turn
                                    ):
                                        yield Move(
                                            start=start,
                                            end=end,
                                            is_capture=False,
                                            is_castle=True,
                                            en_passant=-1,
                                        )
                                    if (
                                        self.turn * castle == CASTLE.QUEEN_SIDE
                                        and start
                                        == (21 if self.turn == COLOR.BLACK else 91)
                                        and self.squares[end] == PIECE.KING * self.turn
                                    ):
                                        yield Move(
                                            start=start,
                                            end=end,
                                            is_capture=False,
                                            is_castle=True,
                                            en_passant=-1,
                                        )

                            if (
                                self.squares[end] != PIECE.INVALID
                                and self.squares[end] * self.turn <= 0
                                and ((not quiescent) or is_capture)  # quiescence check
                            ):
                                yield Move(
                                    start=start,
                                    end=end,
                                    is_capture=is_capture,
                                    is_castle=False,
                                    en_passant=-1,
                                )
                            if self.squares[end] != PIECE.EMPTY or is_capture:
                                break
                if type == PIECE.BISHOP:
                    for direction in [11, -11, 9, -9]:
                        for depl in [x * direction for x in range(1, 8)]:
                            end = start + depl
                            is_capture = (
                                bool(self.squares[end]) or end == self.king_en_passant
                            )
                            if (
                                self.squares[end] != PIECE.INVALID
                                and self.squares[end] * self.turn <= 0
                                and ((not quiescent) or is_capture)  # quiescence check
                            ):
                                yield Move(
                                    start=start,
                                    end=end,
                                    is_capture=is_capture,
                                    is_castle=False,
                                    en_passant=-1,
                                )
                            if self.squares[end] != PIECE.EMPTY or is_capture:
                                break
                if type == PIECE.QUEEN:
                    for direction in [11, -11, 9, -9] + [1, -1, 10, -10]:
                        for depl in [x * direction for x in range(1, 8)]:
                            end = start + depl
                            is_capture = (
                                bool(self.squares[end]) or end == self.king_en_passant
                            )
                            if (
                                self.squares[end] != PIECE.INVALID
                                and self.squares[end] * self.turn <= 0
                                and ((not quiescent) or is_capture)  # quiescence check
                            ):
                                yield Move(
                                    start=start,
                                    end=end,
                                    is_capture=is_capture,
                                    is_castle=False,
                                    en_passant=-1,
                                )
                            if self.squares[end] != PIECE.EMPTY or is_capture:
                                break
                if type == PIECE.KING:
                    for depl in [11, -11, 9, -9] + [1, -1, 10, -10]:
                        end = start + depl
                        is_capture = (
                            bool(self.squares[end]) or end == self.king_en_passant
                        )
                        if (
                            self.squares[end] != PIECE.INVALID
                            and self.squares[end] * self.turn <= 0
                            and ((not quiescent) or is_capture)  # quiescence check
                        ):
                            yield Move(
                                start=start,
                                end=end,
                                is_capture=is_capture,
                                is_castle=False,
                                en_passant=-1,
                            )
                if type == PIECE.PAWN:
                    if not quiescent:
                        depls = [(10 if self.turn == COLOR.BLACK else -10)]
                        if start // 10 == (3 if self.turn == COLOR.BLACK else 8):
                            depls.append((20 if self.turn == COLOR.BLACK else -20))
                        for depl in depls:
                            end = start + depl
                            if self.squares[end] == PIECE.EMPTY:
                                if abs(depl) == 20:
                                    en_passant = start + depls[0]
                                else:
                                    en_passant = -1
                                yield Move(
                                    start=start,
                                    end=end,
                                    is_capture=False,
                                    is_castle=False,
                                    en_passant=en_passant,
                                )
                            else:
                                # do not allow 2 squares move if there's a piece in the way
                                break
                    for depl in [9, 11] if self.turn == COLOR.BLACK else [-9, -11]:
                        end = start + depl
                        if (
                            self.squares[end] != PIECE.INVALID
                            and self.squares[end] * self.turn < 0
                            and (
                                (not quiescent) or end == self.king_en_passant
                            )  # quiescence check
                        ) or end == self.en_passant:
                            yield Move(
                                start=start,
                                end=end,
                                is_capture=True,
                                is_castle=False,
                                en_passant=-1,
                            )
