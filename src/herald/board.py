from dataclasses import dataclass
from typing import Iterable

from .constants import ASCII_REP, CASTLE, COLOR, COLOR_IDX, IS_PIECE, PIECE, get_color
from .data_structures import Move, to_normal_notation, to_square_notation


@dataclass
class Board:
    # list of PIECE * COLOR
    # 120 squares for a 10*12 mailbox
    # https://www.chessprogramming.org/Mailbox
    squares: list[int]
    # color of the player who's turn it is
    turn: COLOR
    # list reprensenting castling rights (index CASTLE + COLOR)
    castling_rights: list
    # the following values are ints with default values
    en_passant: int
    half_move: int
    full_move: int
    king_en_passant: list[int]
    pawn_number: list[int]
    pawn_in_file: list[int]
    king_squares: list[int]
    invturn: COLOR


def to_fen(b: Board) -> str:
    rep = ""
    empty = 0
    for i in range(120):
        if i % 10 == 9 and 20 < i < 91:
            if empty != 0:
                rep += str(empty)
                empty = 0
            rep += "/"
            continue
        if b.squares[i] == PIECE.INVALID:
            continue
        if b.squares[i] == PIECE.EMPTY:
            empty += 1
            continue
        if empty != 0:
            rep += str(empty)
            empty = 0
        rep += f"{ASCII_REP[b.squares[i]]}"
    if empty != 0:
        rep += str(empty)

    rep += " "

    # color to move
    if b.turn == COLOR.BLACK:
        rep += "b"
    else:
        rep += "w"

    rep += " "

    # castling rights
    if b.castling_rights[CASTLE.KING_SIDE + COLOR.WHITE] == 1:
        rep += "K"
    if b.castling_rights[CASTLE.QUEEN_SIDE + COLOR.WHITE] == 1:
        rep += "Q"
    if b.castling_rights[CASTLE.KING_SIDE + COLOR.BLACK] == 1:
        rep += "k"
    if b.castling_rights[CASTLE.QUEEN_SIDE + COLOR.BLACK] == 1:
        rep += "q"
    # if no castling right is remaining
    if rep[-1] == " ":
        rep += "-"

    rep += " "

    # en passant
    if b.en_passant == -1:
        rep += "-"
    else:
        rep += to_normal_notation(b.en_passant)

    rep += " "

    rep += f"{b.half_move} {b.full_move}"

    return rep


def from_uci(b: Board, uci: str) -> Move:
    start = to_square_notation(uci[:2])
    end = to_square_notation(uci[2:])
    return Move(
        start=start,
        end=end,
        is_capture=(
            IS_PIECE[b.squares[end]] != PIECE.EMPTY
            or end == b.en_passant
            or end in b.king_en_passant
        ),
        is_castle=(
            start in (95, 25)
            and IS_PIECE[b.squares[start]] == PIECE.KING
            and abs(end - start) == 2
        ),
        en_passant=(start + end) // 2
        if IS_PIECE[b.squares[start]] == PIECE.PAWN and abs(start - end) == 20
        else -1,
    )


def to_string(b: Board) -> str:
    rep = f"{'w' if b.turn == COLOR.WHITE else 'b'}  0 1 2 3 4 5 6 7 8 9"
    for i in range(120):
        if i % 10 == 0:
            rep += f"\n{i//10:02d} "
        if b.squares[i] == PIECE.INVALID:
            rep += "- "
            continue
        rep += f"{ASCII_REP[b.squares[i]]} "
    return rep


def from_fen(fen: str) -> Board:
    if fen == "startpos":
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    rep, turn, castling_rights, en_passant, half_move, full_move = fen.split()

    cr = [0, 0, 0, 0]
    if "K" in castling_rights:
        cr[CASTLE.KING_SIDE + COLOR.WHITE] = 1
    if "Q" in castling_rights:
        cr[CASTLE.QUEEN_SIDE + COLOR.WHITE] = 1
    if "k" in castling_rights:
        cr[CASTLE.KING_SIDE + COLOR.BLACK] = 1
    if "q" in castling_rights:
        cr[CASTLE.QUEEN_SIDE + COLOR.BLACK] = 1

    squares = [int(PIECE.INVALID)] * 120
    king_squares = [-1, -1]
    s = 19
    for row in rep.split("/"):
        squares[(s := s + 1)] = PIECE.INVALID
        for c in row:
            piece = None
            color = COLOR.BLACK if c.islower() else COLOR.WHITE
            if c.lower() == "r":
                piece = PIECE.ROOK * color
            if c.lower() == "n":
                piece = PIECE.KNIGHT * color
            if c.lower() == "b":
                piece = PIECE.BISHOP * color
            if c.lower() == "q":
                piece = PIECE.QUEEN * color
            if c.lower() == "k":
                piece = PIECE.KING * color
                king_squares[COLOR_IDX[color]] = s + 1
            if c.lower() == "p":
                piece = PIECE.PAWN * color
            if piece is not None:
                squares[(s := s + 1)] = piece
            elif int(c) > 0:
                for _ in range(int(c)):
                    squares[(s := s + 1)] = PIECE.EMPTY
        squares[(s := s + 1)] = PIECE.INVALID

    b = Board(
        squares,
        COLOR.WHITE if turn == "w" else COLOR.BLACK,
        cr,
        (to_square_notation(en_passant) if en_passant != "-" else -1),
        int(half_move),
        int(full_move),
        [],
        get_pawns_stats(squares)[0],
        get_pawns_stats(squares)[1],
        king_squares,
        COLOR.WHITE if turn == "b" else COLOR.BLACK,
    )

    return b


def get_pawns_stats(squares):
    # fmt: off
    # number of pawns for [white, black]
    pawn_number = [0, 0]
    # number of pawns in each file for [white * 10, black * 10]
    pawn_in_file = [
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ]
    # fmt: on

    for i in range(8):
        for j in range(8):
            square = (2 + j) * 10 + (i + 1)
            piece = squares[square]
            if piece in [0, 7]:
                continue
            if IS_PIECE[piece] == PIECE.PAWN:
                color = get_color(piece)
                pawn_number[COLOR_IDX[color]] += 1
                pawn_in_file[(i + 1) + 10 * COLOR_IDX[color]] += 1

    return pawn_number, pawn_in_file


def push(b: Board, move: Move) -> Board:
    squares = b.squares.copy()
    en_passant = b.en_passant
    king_en_passant = []
    castling_rights = b.castling_rights.copy()
    half_move = b.half_move + 1
    pawn_number = b.pawn_number.copy()
    pawn_in_file = b.pawn_in_file.copy()
    king_squares = b.king_squares.copy()
    full_move = b.full_move + 1 if b.turn == COLOR.BLACK else b.full_move

    assert b.squares[move.start] != PIECE.EMPTY, "Moving piece cannot be empty"
    assert IS_PIECE[b.squares[move.start]] != PIECE.INVALID, "Moving piece cannot be invalid"

    piece_start = b.squares[move.start]

    if move.is_capture or IS_PIECE[piece_start] == PIECE.PAWN:
        # reset half_move count when condition is met
        half_move = 0

    if move.is_capture and IS_PIECE[piece_start] == PIECE.PAWN:
        # the moved pawn changes pawn_in_file numbers
        color = get_color(squares[move.start])
        pawn_in_file[(move.start % 10) + 10 * COLOR_IDX[color]] -= 1
        pawn_in_file[(move.end % 10) + 10 * COLOR_IDX[color]] += 1

    if move.is_capture and IS_PIECE[squares[move.end]] == PIECE.PAWN:
        # the pawn taken changes pawn_in_file numbers
        color = get_color(squares[move.end])
        pawn_number[COLOR_IDX[color]] -= 1
        pawn_in_file[(move.end % 10) + 10 * COLOR_IDX[color]] -= 1

    # do the move
    squares[move.start] = PIECE.EMPTY
    squares[move.end] = piece_start

    # change the king square
    if IS_PIECE[piece_start] == PIECE.KING:
        king_squares[COLOR_IDX[b.turn]] = move.end

    # special removal for "en passant" moves
    if move.end == b.en_passant and IS_PIECE[piece_start] == PIECE.PAWN:
        target = move.end + (10 * b.turn)
        color = get_color(squares[target])
        squares[target] = PIECE.EMPTY
        pawn_number[COLOR_IDX[color]] -= 1
        pawn_in_file[(move.end % 10) + 10 * COLOR_IDX[color]] -= 1

    # declare en_passant square for the current board
    if move.en_passant != -1:
        en_passant = move.en_passant
    else:
        en_passant = -1

    # promotion
    if IS_PIECE[piece_start] == PIECE.PAWN and move.end // 10 == (
        2 if b.turn == COLOR.WHITE else 9
    ):
        color = get_color(squares[move.end])
        pawn_number[COLOR_IDX[color]] -= 1
        pawn_in_file[(move.end % 10) + 10 * COLOR_IDX[color]] -= 1
        squares[move.end] = PIECE.QUEEN * b.turn

    # some hardcode for castling move of the rook
    if move.is_castle:
        castling_rights[CASTLE.KING_SIDE + b.turn] = 0
        castling_rights[CASTLE.QUEEN_SIDE + b.turn] = 0
        if move.end == 97:
            squares[98] = PIECE.EMPTY
            squares[95] = PIECE.EMPTY
            squares[96] = PIECE.ROOK * COLOR.WHITE
            king_en_passant.append(96)
            king_en_passant.append(95)
        if move.end == 93:
            squares[91] = PIECE.EMPTY
            squares[95] = PIECE.EMPTY
            squares[94] = PIECE.ROOK * COLOR.WHITE
            king_en_passant.append(94)
            king_en_passant.append(95)
        if move.end == 27:
            squares[28] = PIECE.EMPTY
            squares[25] = PIECE.EMPTY
            squares[26] = PIECE.ROOK * COLOR.BLACK
            king_en_passant.append(26)
            king_en_passant.append(25)
        if move.end == 23:
            squares[21] = PIECE.EMPTY
            squares[25] = PIECE.EMPTY
            squares[24] = PIECE.ROOK * COLOR.BLACK
            king_en_passant.append(24)
            king_en_passant.append(25)
    else:
        # remove castling rights
        if IS_PIECE[piece_start] == PIECE.KING:
            castling_rights[CASTLE.KING_SIDE + b.turn] = 0
            castling_rights[CASTLE.QUEEN_SIDE + b.turn] = 0
        else:
            if move.end == 98 or move.start == 98:
                castling_rights[CASTLE.KING_SIDE + COLOR.WHITE] = 0
            if move.end == 91 or move.start == 91:
                castling_rights[CASTLE.QUEEN_SIDE + COLOR.WHITE] = 0
            if move.end == 28 or move.start == 28:
                castling_rights[CASTLE.KING_SIDE + COLOR.BLACK] = 0
            if move.end == 21 or move.start == 21:
                castling_rights[CASTLE.QUEEN_SIDE + COLOR.BLACK] = 0

    # check that border squares are still invalid
    assert not any(filter(lambda x: x != 7, squares[:20]))
    assert not any(filter(lambda x: x != 7, squares[100:]))
    assert not any(filter(lambda x: x != 7, [v for k, v in enumerate(squares) if k % 10 == 0]))
    assert not any(filter(lambda x: x != 7, [v for k, v in enumerate(squares) if k % 10 == 9]))

    return Board(
        squares,
        COLOR(b.turn * -1),
        castling_rights,
        en_passant,
        half_move,
        full_move,
        king_en_passant,
        pawn_number,
        pawn_in_file,
        king_squares,
        COLOR(b.invturn * -1),
    )


def king_square(b: Board, color: COLOR) -> int | None:
    try:
        return int(b.squares.index(PIECE.KING * color))
    except:
        return None


def number_of(b: Board, piece: PIECE, color: COLOR) -> int:
    try:
        return int(b.squares.count(piece * color))
    except:
        return 0


def is_legal_move(b: Board, move: Move) -> bool:
    # verify that the king of the player to move exists
    if number_of(b, PIECE.KING, b.turn) < 1:
        return False

    b2 = push(b, move)

    # the king should not be in check after the move
    ks = king_square(b2, b2.invturn)
    if ks is None:
        return False

    if is_square_attacked(b2, ks, b2.turn):
        return False

    # the king_en_passant squares should not be in check
    for kep in b2.king_en_passant:
        if is_square_attacked(b2, kep, b2.turn):
            return False

    ks = king_square(b, b.turn)
    if ks is None:
        return False

    # a castling move is only acceptable if the king is not in check
    if move.is_castle and is_square_attacked(b, ks, b.invturn):
        return False

    return True


def legal_moves(b: Board, quiescent: bool = False) -> list[Move]:
    moves = []

    if number_of(b, PIECE.KING, b.turn) < 1:
        return []

    for move in pseudo_legal_moves(b, quiescent):
        if not is_legal_move(b, move):
            continue
        moves.append(move)
    return moves


def is_square_attacked(b: Board, square: int, color: COLOR) -> bool:
    """Detect if square on b is attacked by color."""
    for depl in [21, 12, -8, -19, -21, -12, 8, 19]:
        if b.squares[square + depl] == PIECE.KNIGHT * color:
            return True
    for direction in [1, -1, 10, -10]:
        for x in range(1, 8):
            end = square + x * direction
            if (
                b.squares[end] == PIECE.ROOK * color
                or b.squares[end] == PIECE.QUEEN * color
                or (x == 1 and b.squares[end] == PIECE.KING * color)
            ):
                return True
            if b.squares[end] != PIECE.EMPTY:
                break
    for direction in [11, -11, 9, -9]:
        for x in range(1, 8):
            end = square + x * direction
            if (
                b.squares[end] == PIECE.BISHOP * color
                or b.squares[end] == PIECE.QUEEN * color
                or (x == 1 and b.squares[end] == PIECE.KING * color)
            ):
                return True
            if b.squares[end] != PIECE.EMPTY:
                break
    for depl in [9, 11] if color == COLOR.WHITE else [-9, -11]:
        if b.squares[square + depl] == PIECE.PAWN * color:
            return True
    return False


def _knight_moves(
    b: Board,
    start: int,
    quiescent: bool = False,
) -> Iterable[Move]:
    for depl in [21, 12, -8, -19, -21, -12, 8, 19]:
        end = start + depl
        is_capture = bool(b.squares[end]) or end in b.king_en_passant
        is_king_capture = IS_PIECE[b.squares[end]] == PIECE.KING or end in b.king_en_passant
        if (
            b.squares[end] != PIECE.INVALID
            and b.squares[end] * b.turn <= 0
            and ((not quiescent) or is_capture)  # quiescence check
        ):
            yield Move(
                start=start,
                end=end,
                moving_piece=PIECE.KNIGHT,
                captured_piece=IS_PIECE[b.squares[end]],  # don't take king_en_passant into account
                is_capture=is_capture,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
                is_quiescent=quiescent,
            )


def _rook_moves(
    b: Board,
    start: int,
    quiescent: bool = False,
) -> Iterable[Move]:
    for direction in [1, -1, 10, -10]:
        for x in range(1, 8):
            end = start + x * direction
            is_capture = bool(b.squares[end]) or end in b.king_en_passant
            is_king_capture = IS_PIECE[b.squares[end]] == PIECE.KING or end in b.king_en_passant

            # castling moves are processed here
            # because we are already checking if the path is clear that way
            if not quiescent:
                if (
                    b.castling_rights[CASTLE.KING_SIDE + b.turn] == 1
                    and start == (28 if b.turn == COLOR.BLACK else 98)
                    and b.squares[end] == PIECE.KING * b.turn
                ):
                    yield Move(
                        start=(95 if b.turn == COLOR.WHITE else 25),
                        end=(97 if b.turn == COLOR.WHITE else 27),
                        moving_piece=PIECE.KING,
                        captured_piece=IS_PIECE[
                            b.squares[end]
                        ],  # don't take king_en_passant into account
                        is_capture=False,
                        is_castle=True,
                        en_passant=-1,
                        is_king_capture=False,
                        is_quiescent=quiescent,
                    )
                if (
                    b.castling_rights[CASTLE.QUEEN_SIDE + b.turn] == 1
                    and start == (21 if b.turn == COLOR.BLACK else 91)
                    and b.squares[end] == PIECE.KING * b.turn
                ):
                    yield Move(
                        start=(95 if b.turn == COLOR.WHITE else 25),
                        end=(93 if b.turn == COLOR.WHITE else 23),
                        moving_piece=PIECE.KING,
                        captured_piece=0,
                        is_capture=False,
                        is_castle=True,
                        en_passant=-1,
                        is_king_capture=False,
                        is_quiescent=quiescent,
                    )

            if (
                b.squares[end] != PIECE.INVALID
                and b.squares[end] * b.turn <= 0
                and ((not quiescent) or is_capture)  # quiescence check
            ):
                yield Move(
                    start=start,
                    end=end,
                    moving_piece=PIECE.ROOK,
                    captured_piece=IS_PIECE[b.squares[end]],
                    is_capture=is_capture,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                    is_quiescent=quiescent,
                )
            if b.squares[end] != PIECE.EMPTY or is_capture:
                break


def _bishop_moves(
    b: Board,
    start: int,
    quiescent: bool = False,
) -> Iterable[Move]:
    for direction in [11, -11, 9, -9]:
        for x in range(1, 8):
            end = start + x * direction
            is_capture = bool(b.squares[end]) or end in b.king_en_passant
            is_king_capture = IS_PIECE[b.squares[end]] == PIECE.KING or end in b.king_en_passant
            if (
                b.squares[end] != PIECE.INVALID
                and b.squares[end] * b.turn <= 0
                and ((not quiescent) or is_capture)  # quiescence check
            ):
                yield Move(
                    start=start,
                    end=end,
                    moving_piece=PIECE.BISHOP,
                    captured_piece=IS_PIECE[
                        b.squares[end]
                    ],  # don't take king_en_passant into account
                    is_capture=is_capture,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                    is_quiescent=quiescent,
                )
            if b.squares[end] != PIECE.EMPTY or is_capture:
                break


def _queen_moves(
    b: Board,
    start: int,
    quiescent: bool = False,
) -> Iterable[Move]:
    for direction in [11, -11, 9, -9, 1, -1, 10, -10]:
        for x in range(1, 8):
            end = start + x * direction
            is_capture = bool(b.squares[end]) or end in b.king_en_passant
            is_king_capture = IS_PIECE[b.squares[end]] == PIECE.KING or end in b.king_en_passant
            if (
                b.squares[end] != PIECE.INVALID
                and b.squares[end] * b.turn <= 0
                and ((not quiescent) or is_capture)  # quiescence check
            ):
                yield Move(
                    start=start,
                    end=end,
                    moving_piece=PIECE.QUEEN,
                    captured_piece=IS_PIECE[
                        b.squares[end]
                    ],  # don't take king_en_passant into account
                    is_capture=is_capture,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                    is_quiescent=quiescent,
                )
            if b.squares[end] != PIECE.EMPTY or is_capture:
                break


def _king_moves(
    b: Board,
    start: int,
    quiescent: bool = False,
) -> Iterable[Move]:
    for depl in [11, -11, 9, -9, 1, -1, 10, -10]:
        end = start + depl
        is_capture = bool(b.squares[end]) or end in b.king_en_passant
        is_king_capture = IS_PIECE[b.squares[end]] == PIECE.KING or end in b.king_en_passant
        if (
            b.squares[end] != PIECE.INVALID
            and b.squares[end] * b.turn <= 0
            and ((not quiescent) or is_capture)  # quiescence check
        ):
            yield Move(
                start=start,
                end=end,
                moving_piece=PIECE.KING,
                captured_piece=IS_PIECE[b.squares[end]],  # don't take king_en_passant into account
                is_capture=is_capture,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
                is_quiescent=quiescent,
            )


def _pawn_moves(
    b: Board,
    start: int,
    quiescent: bool = False,
) -> Iterable[Move]:
    if not quiescent:
        depls = [(10 if b.turn == COLOR.BLACK else -10)]
        if start // 10 == (3 if b.turn == COLOR.BLACK else 8):
            depls.append((20 if b.turn == COLOR.BLACK else -20))
        for depl in depls:
            end = start + depl
            if b.squares[end] == PIECE.EMPTY:
                if abs(depl) == 20:
                    en_passant = start + depls[0]
                else:
                    en_passant = -1
                yield Move(
                    start=start,
                    end=end,
                    moving_piece=PIECE.PAWN,
                    captured_piece=0,
                    is_capture=False,
                    is_castle=False,
                    en_passant=en_passant,
                    is_king_capture=False,
                    is_quiescent=quiescent,
                )
            else:
                # do not allow 2 squares move if there's a piece in the way
                break
    for depl in [9, 11] if b.turn == COLOR.BLACK else [-9, -11]:
        end = start + depl
        if (
            (b.squares[end] != PIECE.INVALID and b.squares[end] * b.turn < 0)
            or end == b.en_passant
            or end in b.king_en_passant
        ):
            is_king_capture = IS_PIECE[b.squares[end]] == PIECE.KING or end in b.king_en_passant
            yield Move(
                start=start,
                end=end,
                moving_piece=PIECE.PAWN,
                captured_piece=IS_PIECE[b.squares[end]],  # don't take king_en_passant into account
                is_capture=True,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
                is_quiescent=quiescent,
            )


# Special function to create moves that target a square
# Useful for the SEE function
# is LVA (least valuable attacker) by implementation
def capture_moves(b: Board, target: int) -> Iterable[Move]:
    is_king_capture = IS_PIECE[b.squares[target]] == PIECE.KING

    # PAWN
    for depl in [9, 11] if b.turn == COLOR.WHITE else [-9, -11]:
        start = target + depl
        if IS_PIECE[b.squares[start]] == PIECE.PAWN and b.squares[start] * b.turn > 0:
            yield Move(
                start=start,
                end=target,
                moving_piece=PIECE.PAWN,
                captured_piece=IS_PIECE[b.squares[target]],
                is_capture=True,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
                is_quiescent=True,
            )

    # KNIGHT
    for depl in [21, 12, -8, -19, -21, -12, 8, 19]:
        start = target + depl
        if IS_PIECE[b.squares[start]] == PIECE.KNIGHT and b.squares[start] * b.turn > 0:
            yield Move(
                start=start,
                end=target,
                moving_piece=PIECE.KNIGHT,
                captured_piece=IS_PIECE[b.squares[target]],
                is_capture=True,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
                is_quiescent=True,
            )

    # BISHOP
    for direction in [11, -11, 9, -9]:
        for x in range(1, 8):
            start = target + x * direction

            if (IS_PIECE[b.squares[start]] == PIECE.BISHOP) and b.squares[start] * b.turn > 0:
                yield Move(
                    start=start,
                    end=target,
                    moving_piece=IS_PIECE[b.squares[start]],
                    captured_piece=IS_PIECE[b.squares[target]],
                    is_capture=True,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                    is_quiescent=True,
                )
            if b.squares[start] != PIECE.EMPTY:
                break

    # ROOK
    for direction in [1, -1, 10, -10]:
        for x in range(1, 8):
            start = target + x * direction

            if (IS_PIECE[b.squares[start]] == PIECE.ROOK) and b.squares[start] * b.turn > 0:
                yield Move(
                    start=start,
                    end=target,
                    moving_piece=IS_PIECE[b.squares[start]],
                    captured_piece=IS_PIECE[b.squares[target]],
                    is_capture=True,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                    is_quiescent=True,
                )
            if b.squares[start] != PIECE.EMPTY:
                break

    # QUEEN (DIAGONALS)
    for direction in [11, -11, 9, -9]:
        for x in range(1, 8):
            start = target + x * direction

            if (IS_PIECE[b.squares[start]] == PIECE.QUEEN) and b.squares[start] * b.turn > 0:
                yield Move(
                    start=start,
                    end=target,
                    moving_piece=PIECE.QUEEN,
                    captured_piece=IS_PIECE[b.squares[target]],
                    is_capture=True,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                    is_quiescent=True,
                )
            if b.squares[start] != PIECE.EMPTY:
                break

    # QUEEN (VERTICAL + HORIZONTAL)
    for direction in [1, -1, 10, -10]:
        for x in range(1, 8):
            start = target + x * direction

            if (IS_PIECE[b.squares[start]] == PIECE.QUEEN) and b.squares[start] * b.turn > 0:
                yield Move(
                    start=start,
                    end=target,
                    moving_piece=PIECE.QUEEN,
                    captured_piece=IS_PIECE[b.squares[target]],
                    is_capture=True,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                    is_quiescent=True,
                )
            if b.squares[start] != PIECE.EMPTY:
                break

    # KING
    for depl in [11, -11, 9, -9, 1, -1, 10, -10]:
        start = target + depl
        if IS_PIECE[b.squares[start]] == PIECE.KING and b.squares[start] * b.turn > 0:
            yield Move(
                start=start,
                end=target,
                moving_piece=PIECE.KING,
                captured_piece=IS_PIECE[b.squares[target]],
                is_capture=True,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
                is_quiescent=True,
            )


def will_check_the_king(b: Board, move: Move) -> bool:
    b2 = push(b, move)
    if is_square_attacked(b2, b2.king_squares[COLOR_IDX[b2.turn]], b2.invturn):
        return True
    return False


def king_is_in_check(b: Board, color: COLOR) -> bool:
    if is_square_attacked(b, b.king_squares[COLOR_IDX[color]], COLOR(color * -1)):
        return True
    return False


def pseudo_legal_moves(
    b: Board,
    quiescent: bool = False,
) -> Iterable[Move]:
    for start, piece in enumerate(b.squares[20:100]):
        if piece == PIECE.INVALID or piece * b.turn < 0:
            continue
        start = start + 20
        piece_type = IS_PIECE[piece]
        if piece_type == PIECE.PAWN:
            for move in _pawn_moves(b, start, quiescent):
                yield move
        if piece_type == PIECE.KNIGHT:
            for move in _knight_moves(b, start, quiescent):
                yield move
        if piece_type == PIECE.BISHOP:
            for move in _bishop_moves(b, start, quiescent):
                yield move
        if piece_type == PIECE.ROOK:
            for move in _rook_moves(b, start, quiescent):
                yield move
        if piece_type == PIECE.QUEEN:
            for move in _queen_moves(b, start, quiescent):
                yield move
        if piece_type == PIECE.KING:
            for move in _king_moves(b, start, quiescent):
                yield move
