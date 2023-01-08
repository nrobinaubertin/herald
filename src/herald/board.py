from array import array
from typing import Hashable, Iterable

from herald.constants import ASCII_REP, CASTLE, COLOR, PIECE
from herald.data_structures import Board, Move, to_normal_notation, to_square_notation


def invturn(b: Board) -> COLOR:
    return COLOR.WHITE if b.turn == COLOR.BLACK else COLOR.BLACK


# get position as a byte object for comparison purposes
def get_pos(b: Board) -> Hashable:
    pos = array("b")
    pos.extend(b.squares)
    pos.append(b.turn)
    pos.extend(b.castling_rights)
    pos.append(b.en_passant)
    pos.append(b.king_en_passant)
    return pos.tobytes()


def to_fen(b: Board) -> str:

    rep = ""
    empty = 0
    for i in range(120):
        if i % 10 == 9 and i > 20 and i < 91:
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
            abs(b.squares[end]) != PIECE.EMPTY or end == b.en_passant or end == b.king_en_passant
        ),
        is_castle=(
            start in (95, 25) and abs(b.squares[start]) == PIECE.KING and abs(end - start) == 2
        ),
        en_passant=(start + end) // 2
        if abs(b.squares[start]) == PIECE.PAWN and abs(start - end) == 20
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

    cr = array("b", [0, 0, 0, 0])
    if "K" in castling_rights:
        cr[CASTLE.KING_SIDE + COLOR.WHITE] = 1
    if "Q" in castling_rights:
        cr[CASTLE.QUEEN_SIDE + COLOR.WHITE] = 1
    if "k" in castling_rights:
        cr[CASTLE.KING_SIDE + COLOR.BLACK] = 1
    if "q" in castling_rights:
        cr[CASTLE.QUEEN_SIDE + COLOR.BLACK] = 1

    squares = array("b", [PIECE.INVALID] * 120)
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
            if c.lower() == "p":
                piece = PIECE.PAWN * color
            if piece is not None:
                squares[(s := s + 1)] = piece
            elif int(c) > 0:
                for _ in range(int(c)):
                    squares[(s := s + 1)] = PIECE.EMPTY
        squares[(s := s + 1)] = PIECE.INVALID

    b = Board(
        squares=squares,
        positions_history=set(),
        turn=COLOR.WHITE if turn == "w" else COLOR.BLACK,
        castling_rights=cr,
        en_passant=(to_square_notation(en_passant) if en_passant != "-" else -1),
        half_move=int(half_move),
        full_move=int(full_move),
        pawn_number=get_pawns_stats(squares)[0],
        pawn_in_file=get_pawns_stats(squares)[1],
    )

    return b


def get_pawns_stats(squares):

    pawn_number = array("b", [0, 0])
    pawn_in_file = array(
        "b",
        [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ],
    )

    for i in range(8):
        for j in range(8):
            square = (2 + j) * 10 + (i + 1)
            piece = squares[square]
            if piece == 0 or piece == 7:
                continue
            if abs(piece) == PIECE.PAWN:
                color = abs(piece) // piece
                pawn_number[(color + 1) // 2] += 1
                pawn_in_file[i * 2 + (color + 1) // 2] += 1

    return pawn_number, pawn_in_file


def push(b: Board, move: Move) -> Board:

    squares = array("b", b.squares)
    en_passant = b.en_passant
    king_en_passant = b.king_en_passant
    castling_rights = array("b", b.castling_rights)
    half_move = b.half_move
    pawn_number = array("b", b.pawn_in_file)
    pawn_in_file = array("b", b.pawn_in_file)

    if move.is_null:
        return Board(
            squares=squares,
            positions_history=b.positions_history,
            turn=invturn(b),
            castling_rights=castling_rights,
            en_passant=-1,
            half_move=half_move + 1,
            full_move=b.full_move + 1,
            king_en_passant=-1,
        )

    assert b.squares[move.start] != PIECE.EMPTY, "Moving piece cannot be empty"
    assert abs(b.squares[move.start]) != PIECE.INVALID, "Moving piece cannot be invalid"

    piece_start = b.squares[move.start]

    # reset half_move count when condition is met
    if move.is_capture or abs(piece_start) == PIECE.PAWN:
        half_move = 0
        color = abs(squares[move.start]) // squares[move.start]
        pawn_in_file[(move.start % 10) * 2 + (color + 1) // 2] -= 1
        pawn_in_file[(move.end % 10) * 2 + (color + 1) // 2] += 1

    if move.is_capture and abs(squares[move.end]) == PIECE.PAWN:
        color = abs(squares[move.end]) // squares[move.end]
        pawn_number[(color + 1) // 2] -= 1
        pawn_in_file[(move.end % 10) * 2 + (color + 1) // 2] -= 1

    # do the move
    squares[move.start] = PIECE.EMPTY
    squares[move.end] = piece_start

    # special removal for "en passant" moves
    if move.end == b.en_passant and abs(piece_start) == PIECE.PAWN:
        target = move.end + (10 * b.turn)
        color = abs(squares[target]) // squares[target]
        squares[target] = PIECE.EMPTY
        pawn_number[(color + 1) // 2] -= 1
        pawn_in_file[(move.end % 10) * 2 + (color + 1) // 2] -= 1

    # declare en_passant square for the current board
    if move.en_passant != -1:
        en_passant = move.en_passant
    else:
        en_passant = -1

    # promotion
    if abs(piece_start) == PIECE.PAWN and move.end // 10 == (2 if b.turn == COLOR.WHITE else 9):
        color = abs(squares[move.end]) // squares[move.end]
        pawn_number[(color + 1) // 2] -= 1
        pawn_in_file[(move.end % 10) * 2 + (color + 1) // 2] -= 1
        squares[move.end] = PIECE.QUEEN * b.turn

    # some hardcode for castling move of the rook
    if move.is_castle:
        castling_rights[CASTLE.KING_SIDE + b.turn] = 0
        castling_rights[CASTLE.QUEEN_SIDE + b.turn] = 0
        if move.end == 97:
            squares[98] = PIECE.EMPTY
            squares[95] = PIECE.EMPTY
            squares[96] = PIECE.ROOK * COLOR.WHITE
            king_en_passant = 96
        if move.end == 93:
            squares[91] = PIECE.EMPTY
            squares[95] = PIECE.EMPTY
            squares[94] = PIECE.ROOK * COLOR.WHITE
            king_en_passant = 94
        if move.end == 27:
            squares[28] = PIECE.EMPTY
            squares[25] = PIECE.EMPTY
            squares[26] = PIECE.ROOK * COLOR.BLACK
            king_en_passant = 26
        if move.end == 23:
            squares[21] = PIECE.EMPTY
            squares[25] = PIECE.EMPTY
            squares[24] = PIECE.ROOK * COLOR.BLACK
            king_en_passant = 24
    else:
        king_en_passant = -1

        # remove castling rights
        if abs(piece_start) == PIECE.KING:
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

    return Board(
        squares=squares,
        positions_history=(b.positions_history | {get_pos(b)} if half_move == 0 else {get_pos(b)}),
        turn=invturn(b),
        castling_rights=castling_rights,
        en_passant=en_passant,
        half_move=half_move + 1,
        full_move=b.full_move + 1,
        king_en_passant=king_en_passant,
        pawn_number=pawn_number,
        pawn_in_file=pawn_in_file,
    )


def king_square(b: Board, color: COLOR) -> int | None:
    try:
        return int(b.squares.index(PIECE.KING * color))
    except:
        return None


def number_of(b: Board, type: PIECE, color: COLOR) -> int:
    try:
        return int(b.squares.count(type * color))
    except:
        return 0


def is_legal_move(b: Board, move: Move) -> bool:

    # verify that the king of the player to move exists
    if number_of(b, PIECE.KING, b.turn) < 1:
        return False

    b2 = push(b, move)

    # the king should not be in check after the move
    ks = king_square(b2, invturn(b2))
    if ks is None:
        return False

    if is_square_attacked(b2, ks, b2.turn):
        return False

    # the king_en_passant square should not be in check
    if b2.king_en_passant != -1 and is_square_attacked(b2, b2.king_en_passant, b2.turn):
        return False

    ks = king_square(b, b.turn)
    if ks is None:
        return False

    # a castling move is only acceptable if the king is not in check
    if move.is_castle and is_square_attacked(b, ks, invturn(b)):
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


# filter out squares with pieces of given type and color
def pieces(
    b: Board,
    type: PIECE | None = None,
    color: COLOR | None = None,
) -> Iterable[int]:
    squares: Iterable[int] = map(
        lambda x: x[0] + 20,
        filter(lambda x: abs(x[1]) in [1, 2, 3, 4, 5, 6], enumerate(b.squares[20:100])),
    )
    if type is not None:
        squares = filter(lambda x: abs(b.squares[x]) == type, squares)
    if color is not None:
        squares = filter(lambda x: b.squares[x] * color > 0, squares)
    return squares


def knight_moves(
    b: Board,
    start: int,
    quiescent: bool = False,
) -> Iterable[Move]:
    for depl in [21, 12, -8, -19, -21, -12, 8, 19]:
        end = start + depl
        is_capture = bool(b.squares[end]) or end == b.king_en_passant
        is_king_capture = abs(b.squares[end]) == PIECE.KING or end == b.king_en_passant
        if (
            b.squares[end] != PIECE.INVALID
            and b.squares[end] * b.turn <= 0
            and ((not quiescent) or is_capture)  # quiescence check
        ):
            yield Move(
                start=start,
                end=end,
                moving_piece=PIECE.KNIGHT * b.turn,
                captured_piece=abs(b.squares[end]),  # don't take king_en_passant into account
                is_capture=is_capture,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
                is_quiescent=quiescent,
            )


def rook_moves(
    b: Board,
    start: int,
    quiescent: bool = False,
) -> Iterable[Move]:
    for direction in [1, -1, 10, -10]:
        for x in range(1, 8):
            end = start + x * direction
            is_capture = bool(b.squares[end]) or end == b.king_en_passant
            is_king_capture = abs(b.squares[end]) == PIECE.KING or end == b.king_en_passant

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
                        moving_piece=PIECE.KING * b.turn,
                        captured_piece=abs(
                            b.squares[end]
                        ),  # don't take king_en_passant into account
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
                        moving_piece=PIECE.KING * b.turn,
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
                    moving_piece=PIECE.ROOK * b.turn,
                    captured_piece=abs(b.squares[end]),
                    is_capture=is_capture,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                    is_quiescent=quiescent,
                )
            if b.squares[end] != PIECE.EMPTY or is_capture:
                break


def bishop_moves(
    b: Board,
    start: int,
    quiescent: bool = False,
) -> Iterable[Move]:
    for direction in [11, -11, 9, -9]:
        for x in range(1, 8):
            end = start + x * direction
            is_capture = bool(b.squares[end]) or end == b.king_en_passant
            is_king_capture = abs(b.squares[end]) == PIECE.KING or end == b.king_en_passant
            if (
                b.squares[end] != PIECE.INVALID
                and b.squares[end] * b.turn <= 0
                and ((not quiescent) or is_capture)  # quiescence check
            ):
                yield Move(
                    start=start,
                    end=end,
                    moving_piece=PIECE.BISHOP * b.turn,
                    captured_piece=abs(b.squares[end]),  # don't take king_en_passant into account
                    is_capture=is_capture,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                    is_quiescent=quiescent,
                )
            if b.squares[end] != PIECE.EMPTY or is_capture:
                break


def queen_moves(
    b: Board,
    start: int,
    quiescent: bool = False,
) -> Iterable[Move]:
    for direction in [11, -11, 9, -9, 1, -1, 10, -10]:
        for x in range(1, 8):
            end = start + x * direction
            is_capture = bool(b.squares[end]) or end == b.king_en_passant
            is_king_capture = abs(b.squares[end]) == PIECE.KING or end == b.king_en_passant
            if (
                b.squares[end] != PIECE.INVALID
                and b.squares[end] * b.turn <= 0
                and ((not quiescent) or is_capture)  # quiescence check
            ):
                yield Move(
                    start=start,
                    end=end,
                    moving_piece=PIECE.QUEEN * b.turn,
                    captured_piece=abs(b.squares[end]),  # don't take king_en_passant into account
                    is_capture=is_capture,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                    is_quiescent=quiescent,
                )
            if b.squares[end] != PIECE.EMPTY or is_capture:
                break


def king_moves(
    b: Board,
    start: int,
    quiescent: bool = False,
) -> Iterable[Move]:
    for depl in [11, -11, 9, -9, 1, -1, 10, -10]:
        end = start + depl
        is_capture = bool(b.squares[end]) or end == b.king_en_passant
        is_king_capture = abs(b.squares[end]) == PIECE.KING or end == b.king_en_passant
        if (
            b.squares[end] != PIECE.INVALID
            and b.squares[end] * b.turn <= 0
            and ((not quiescent) or is_capture)  # quiescence check
        ):
            yield Move(
                start=start,
                end=end,
                moving_piece=PIECE.KING * b.turn,
                captured_piece=abs(b.squares[end]),  # don't take king_en_passant into account
                is_capture=is_capture,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
                is_quiescent=quiescent,
            )


def pawn_moves(
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
                    moving_piece=PIECE.PAWN * b.turn,
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
            or end == b.king_en_passant
        ):
            is_king_capture = abs(b.squares[end]) == PIECE.KING or end == b.king_en_passant
            yield Move(
                start=start,
                end=end,
                moving_piece=PIECE.PAWN * b.turn,
                captured_piece=abs(b.squares[end]),  # don't take king_en_passant into account
                is_capture=True,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
                is_quiescent=quiescent,
            )


# Special function to create moves that target a square
# Useful for the SEE function
def capture_moves(b: Board, target: int) -> Iterable[Move]:

    is_king_capture = abs(b.squares[target]) == PIECE.KING

    # PAWN
    for depl in [9, 11] if b.turn == COLOR.WHITE else [-9, -11]:
        start = target + depl
        if abs(b.squares[start]) == PIECE.PAWN and b.squares[start] * b.turn > 0:
            yield Move(
                start=start,
                end=target,
                moving_piece=PIECE.PAWN * b.turn,
                captured_piece=abs(b.squares[target]),
                is_capture=True,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
                is_quiescent=True,
            )

    # KNIGHT
    for depl in [21, 12, -8, -19, -21, -12, 8, 19]:
        start = target + depl
        if abs(b.squares[start]) == PIECE.KNIGHT and b.squares[start] * b.turn > 0:
            yield Move(
                start=start,
                end=target,
                moving_piece=PIECE.KNIGHT * b.turn,
                captured_piece=abs(b.squares[target]),
                is_capture=True,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
                is_quiescent=True,
            )

    # BISHOP + QUEEN
    for direction in [11, -11, 9, -9]:
        for x in range(1, 8):
            start = target + x * direction

            if (
                abs(b.squares[start]) == PIECE.BISHOP or abs(b.squares[start]) == PIECE.QUEEN
            ) and b.squares[start] * b.turn > 0:
                yield Move(
                    start=start,
                    end=target,
                    moving_piece=abs(b.squares[start]) * b.turn,
                    captured_piece=abs(b.squares[target]),
                    is_capture=True,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                    is_quiescent=True,
                )
            if b.squares[start] != PIECE.EMPTY:
                break

    # ROOK + QUEEN
    for direction in [1, -1, 10, -10]:
        for x in range(1, 8):
            start = target + x * direction

            if (
                abs(b.squares[start]) == PIECE.ROOK or abs(b.squares[start]) == PIECE.QUEEN
            ) and b.squares[start] * b.turn > 0:
                yield Move(
                    start=start,
                    end=target,
                    moving_piece=abs(b.squares[start]) * b.turn,
                    captured_piece=abs(b.squares[target]),
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
        if abs(b.squares[start]) == PIECE.KING and b.squares[start] * b.turn > 0:
            yield Move(
                start=start,
                end=target,
                moving_piece=PIECE.KING * b.turn,
                captured_piece=abs(b.squares[target]),
                is_capture=True,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
                is_quiescent=True,
            )


def pseudo_legal_moves(
    b: Board,
    quiescent: bool = False,
) -> Iterable[Move]:

    # null move
    if quiescent:
        yield Move(
            start=0,
            end=0,
            moving_piece=0,
            is_capture=False,
            is_castle=False,
            en_passant=-1,
            is_king_capture=False,
            is_null=True,
            is_quiescent=quiescent,
        )

    for start, piece in filter(
        lambda x: x[1] != PIECE.INVALID and x[1] * b.turn > 0, enumerate(b.squares[20:100])
    ):
        start = start + 20
        type = abs(piece)
        if type == PIECE.PAWN:
            for move in pawn_moves(b, start, quiescent):
                yield move
        if type == PIECE.KNIGHT:
            for move in knight_moves(b, start, quiescent):
                yield move
        if type == PIECE.BISHOP:
            for move in bishop_moves(b, start, quiescent):
                yield move
        if type == PIECE.ROOK:
            for move in rook_moves(b, start, quiescent):
                yield move
        if type == PIECE.QUEEN:
            for move in queen_moves(b, start, quiescent):
                yield move
        if type == PIECE.KING:
            for move in king_moves(b, start, quiescent):
                yield move
