import collections
from array import array
import hashlib
from . import evaluation
from .constants import PIECE, COLOR, ASCII_REP, CASTLE
from .data_structures import Move, Board


def invturn(board: Board) -> COLOR:
    return COLOR.WHITE if board.turn == COLOR.BLACK else COLOR.BLACK


def from_uci(board: Board, uci: str) -> Move:
    uci = uci.lower()
    digits = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6, "g": 7, "h": 8}
    start = digits[uci[0]] + (10 - int(uci[1])) * 10
    end = digits[uci[2]] + (10 - int(uci[3])) * 10
    return Move(
        start=start,
        end=end,
        is_capture=(
            abs(board.squares[end]) != PIECE.EMPTY
            or end == board.en_passant
            or end == board.king_en_passant
        ),
        is_castle=(
            start in (95, 25)
            and abs(board.squares[start]) == PIECE.KING
            and abs(end - start) == 2
        ),
        en_passant=(start + end) // 2
        if abs(board.squares[start]) == PIECE.PAWN and abs(start - end) == 20
        else -1,
    )


def to_string(board: Board) -> str:
    rep = f"{'w' if board.turn == COLOR.WHITE else 'b'}  0 1 2 3 4 5 6 7 8 9"
    for i in range(120):
        if i % 10 == 0:
            rep += f"\n{i//10:02d} "
        if board.squares[i] == PIECE.INVALID:
            rep += "- "
            continue
        rep += f"{ASCII_REP[board.squares[i]]} "
    return rep


def hash(board: Board):
    data = array("b")
    data.extend(board.squares)
    data.append(board.turn)
    data.extend(board.castling_rights)
    data.append(board.en_passant)
    data.append(board.king_en_passant)
    # return data.tobytes()
    # return data
    return hashlib.sha256(data).hexdigest()


def from_fen(fen: str) -> Board:
    if fen == "startpos":
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    board, turn, castling_rights, en_passant, half_move, full_move = fen.split()

    cr = array('b')
    if "K" in castling_rights:
        cr.append(CASTLE.KING_SIDE * COLOR.WHITE)
    if "Q" in castling_rights:
        cr.append(CASTLE.QUEEN_SIDE * COLOR.WHITE)
    if "k" in castling_rights:
        cr.append(CASTLE.KING_SIDE * COLOR.BLACK)
    if "q" in castling_rights:
        cr.append(CASTLE.QUEEN_SIDE * COLOR.BLACK)

    squares = array("b", [PIECE.INVALID] * 120)
    s = 19
    for row in board.split("/"):
        squares[s := s + 1] = PIECE.INVALID
        for c in row:
            piece = None
            if c.lower() == "r":
                piece = PIECE.ROOK * (COLOR.BLACK if c.islower() else COLOR.WHITE)
            if c.lower() == "n":
                piece = PIECE.KNIGHT * (COLOR.BLACK if c.islower() else COLOR.WHITE)
            if c.lower() == "b":
                piece = PIECE.BISHOP * (COLOR.BLACK if c.islower() else COLOR.WHITE)
            if c.lower() == "q":
                piece = PIECE.QUEEN * (COLOR.BLACK if c.islower() else COLOR.WHITE)
            if c.lower() == "k":
                piece = PIECE.KING * (COLOR.BLACK if c.islower() else COLOR.WHITE)
            if c.lower() == "p":
                piece = PIECE.PAWN * (COLOR.BLACK if c.islower() else COLOR.WHITE)
            if piece is not None:
                squares[s := s + 1] = piece
            elif int(c) > 0:
                for _ in range(int(c)):
                    squares[s := s + 1] = PIECE.EMPTY
        squares[s := s + 1] = PIECE.INVALID

    return Board(
        squares=squares,
        turn=COLOR.WHITE if turn == "w" else COLOR.BLACK,
        castling_rights=cr,
        en_passant=-1,  # TODO
        half_move=int(half_move),
        full_move=int(full_move),
        moves_history=collections.deque(),
        king_en_passant=-1,
    )


def push(board: Board, move: Move) -> Board:

    squares = array('b', board.squares)
    turn = board.turn
    en_passant = board.en_passant
    king_en_passant = board.king_en_passant
    castling_rights = board.castling_rights
    half_move = board.half_move
    full_move = board.full_move
    moves_history = board.moves_history.copy()
    assert board.squares[move.start] != 0, "Moving piece cannot be empty"
    assert abs(board.squares[move.start]) != 7, "Moving piece cannot be invalid"
    value = evaluation.new_value(board, move)

    piece_start = board.squares[move.start]
    assert piece_start != 0, "The starting square cannot be empty"

    squares[move.start] = PIECE.EMPTY
    squares[move.end] = piece_start

    # special removal for "en passant" moves
    if abs(piece_start) == PIECE.PAWN and move.end == board.en_passant:
        target = move.end + (10 * board.turn)
        target_piece = squares[target]
        squares[target] = PIECE.EMPTY

    # declare en_passant square for the current board
    if move.en_passant != -1:
        en_passant = move.en_passant
    else:
        en_passant = -1

    # w/    1258483   11.850    0.000   13.796    0.000 board.py:150(push)
    # w/o   1258483   11.494    0.000   13.353    0.000 board.py:150(push)
    # promotion
    if abs(piece_start) == PIECE.PAWN and move.end // 10 == (
        2 if board.turn == COLOR.WHITE else 9
    ):
        squares[move.end] = PIECE.QUEEN * board.turn

    # w/    1258483   11.850    0.000   13.796    0.000 board.py:150(push)
    # w/o   1258483   11.700    0.000   13.624    0.000 board.py:150(push)
    # some hardcode for castling move of the rook
    if move.is_castle:
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

    # w/    1258483   11.850    0.000   13.796    0.000 board.py:150(push)
    # w/o   1258749    9.942    0.000   11.804    0.000 board.py:150(push)
    try:
        # remove castling rights
        if (
            move.end == 98
            or move.start == 98
            or piece_start == PIECE.KING * COLOR.WHITE
        ):
            castling_rights.remove(CASTLE.KING_SIDE * COLOR.WHITE)
        if (
            move.end == 91
            or move.start == 91
            or piece_start == PIECE.KING * COLOR.WHITE
        ):
            castling_rights.remove(CASTLE.QUEEN_SIDE * COLOR.WHITE)
        if (
            move.end == 28
            or move.start == 28
            or piece_start == PIECE.KING * COLOR.BLACK
        ):
            castling_rights.remove(CASTLE.KING_SIDE * COLOR.BLACK)
        if (
            move.end == 21
            or move.start == 21
            or piece_start == PIECE.KING * COLOR.BLACK
        ):
            castling_rights.remove(CASTLE.QUEEN_SIDE * COLOR.BLACK)
    except ValueError:
        pass

    moves_history.append(move)
    turn = invturn(board)
    half_move += 1
    full_move += 1

    return Board(
        squares=squares,
        turn=turn,
        castling_rights=castling_rights,
        en_passant=en_passant,
        half_move=half_move,
        full_move=full_move,
        moves_history=moves_history,
        king_en_passant=king_en_passant,
        value=value,
    )


def king_square(b: Board, color: COLOR) -> int:
    return b.squares.index(PIECE.KING * color)


def moves(board: Board, quiescent: bool = False) -> list[Move]:
    moves = []
    for move in pseudo_legal_moves(board, quiescent):
        b = push(board, move)

        if (
            not is_square_attacked(b, king_square(b, invturn(b)), b.turn)
        ) and (
            b.king_en_passant == -1
            or not is_square_attacked(b, b.king_en_passant, b.turn)
        ):
            moves.append(move)
    return moves


def is_square_attacked(board: Board, square: int, color: COLOR) -> bool:
    for depl in [21, 12, -8, -19, -21, -12, 8, 19]:
        if board.squares[square + depl] == PIECE.KNIGHT * color:
            return True
    for direction in [1, -1, 10, -10]:
        for depl in [x * direction for x in range(1, 7)]:
            end = square + depl
            if board.squares[end] == PIECE.ROOK * color:
                return True
            if board.squares[end] != PIECE.EMPTY:
                break
    for direction in [11, -11, 9, -9]:
        for depl in [x * direction for x in range(1, 7)]:
            end = square + depl
            if board.squares[end] == PIECE.BISHOP * color:
                return True
            if board.squares[end] != PIECE.EMPTY:
                break
    for direction in [11, -11, 9, -9] + [1, -1, 10, -10]:
        for depl in [x * direction for x in range(1, 7)]:
            end = square + depl
            if board.squares[end] == PIECE.QUEEN * color:
                return True
            if board.squares[end] != PIECE.EMPTY:
                break
    for depl in [11, -11, 9, -9] + [1, -1, 10, -10]:
        if board.squares[square + depl] == PIECE.KING * color:
            return True
    for depl in [9, 11] if color == COLOR.WHITE else [-9, -11]:
        if board.squares[square + depl] == PIECE.PAWN * color:
            return True
    return False


# filter out squares with pieces of given type and color
def pieces(b: Board, type: PIECE | None = None, color: COLOR | None = None):
    squares = range(120)
    squares = filter(
        lambda x: abs(b.squares[x]) != PIECE.INVALID and b.squares[x] != PIECE.EMPTY,
        squares
    )
    if type is not None:
        squares = filter(
            lambda x: abs(b.squares[x]) == type,
            squares
        )
    if color is not None:
        squares = filter(
            lambda x: b.squares[x] * color > 0,
            squares
        )
    return squares

def pseudo_legal_moves(board: Board, quiescent: bool = False):
    for start, type in [(s, abs(p)) for s, p in enumerate(board.squares) if p != 7 and p * board.turn > 0]:
        if type == PIECE.KNIGHT:
            for depl in [21, 12, -8, -19, -21, -12, 8, 19]:
                end = start + depl
                is_capture = (
                    bool(board.squares[end]) or end == board.king_en_passant
                )
                is_king_capture = (
                    abs(board.squares[end]) == PIECE.KING or end == board.king_en_passant
                )
                if (
                    board.squares[end] != PIECE.INVALID
                    and board.squares[end] * board.turn <= 0
                    and ((not quiescent) or is_capture)  # quiescence check
                ):
                    yield Move(
                        start=start,
                        end=end,
                        moving_piece=type * board.turn,
                        is_capture=is_capture,
                        is_castle=False,
                        en_passant=-1,
                        is_king_capture=is_king_capture
                    )
        if type == PIECE.ROOK:
            for direction in [1, -1, 10, -10]:
                for depl in [x * direction for x in range(1, 8)]:
                    end = start + depl
                    is_capture = (
                        bool(board.squares[end]) or end == board.king_en_passant
                    )
                    is_king_capture = (
                        abs(board.squares[end]) == PIECE.KING or end == board.king_en_passant
                    )

                    # castling
                    if not quiescent:
                        for castle in board.castling_rights:
                            if (
                                board.turn * castle == CASTLE.KING_SIDE
                                and start
                                == (28 if board.turn == COLOR.BLACK else 98)
                                and board.squares[end] == PIECE.KING * board.turn
                            ):
                                yield Move(
                                    start=start,
                                    end=end,
                                    moving_piece=type * board.turn,
                                    is_capture=False,
                                    is_castle=True,
                                    en_passant=-1,
                                    is_king_capture=is_king_capture,
                                )
                            if (
                                board.turn * castle == CASTLE.QUEEN_SIDE
                                and start
                                == (21 if board.turn == COLOR.BLACK else 91)
                                and board.squares[end] == PIECE.KING * board.turn
                            ):
                                yield Move(
                                    start=start,
                                    end=end,
                                    moving_piece=type * board.turn,
                                    is_capture=False,
                                    is_castle=True,
                                    en_passant=-1,
                                    is_king_capture=is_king_capture,
                                )

                    if (
                        board.squares[end] != PIECE.INVALID
                        and board.squares[end] * board.turn <= 0
                        and ((not quiescent) or is_capture)  # quiescence check
                    ):
                        yield Move(
                            start=start,
                            end=end,
                            moving_piece=type * board.turn,
                            is_capture=is_capture,
                            is_castle=False,
                            en_passant=-1,
                            is_king_capture=is_king_capture,
                        )
                    if board.squares[end] != PIECE.EMPTY or is_capture:
                        break
        if type == PIECE.BISHOP:
            for direction in [11, -11, 9, -9]:
                for depl in [x * direction for x in range(1, 8)]:
                    end = start + depl
                    is_capture = (
                        bool(board.squares[end]) or end == board.king_en_passant
                    )
                    is_king_capture = (
                        abs(board.squares[end]) == PIECE.KING or end == board.king_en_passant
                    )
                    if (
                        board.squares[end] != PIECE.INVALID
                        and board.squares[end] * board.turn <= 0
                        and ((not quiescent) or is_capture)  # quiescence check
                    ):
                        yield Move(
                            start=start,
                            end=end,
                            moving_piece=type * board.turn,
                            is_capture=is_capture,
                            is_castle=False,
                            en_passant=-1,
                            is_king_capture=is_king_capture,
                        )
                    if board.squares[end] != PIECE.EMPTY or is_capture:
                        break
        if type == PIECE.QUEEN:
            for direction in [11, -11, 9, -9] + [1, -1, 10, -10]:
                for depl in [x * direction for x in range(1, 8)]:
                    end = start + depl
                    is_capture = (
                        bool(board.squares[end]) or end == board.king_en_passant
                    )
                    is_king_capture = (
                        abs(board.squares[end]) == PIECE.KING or end == board.king_en_passant
                    )
                    if (
                        board.squares[end] != PIECE.INVALID
                        and board.squares[end] * board.turn <= 0
                        and ((not quiescent) or is_capture)  # quiescence check
                    ):
                        yield Move(
                            start=start,
                            end=end,
                            moving_piece=type * board.turn,
                            is_capture=is_capture,
                            is_castle=False,
                            en_passant=-1,
                            is_king_capture=is_king_capture,
                        )
                    if board.squares[end] != PIECE.EMPTY or is_capture:
                        break
        if type == PIECE.KING:
            for depl in [11, -11, 9, -9] + [1, -1, 10, -10]:
                end = start + depl
                is_capture = (
                    bool(board.squares[end]) or end == board.king_en_passant
                )
                is_king_capture = (
                    abs(board.squares[end]) == PIECE.KING or end == board.king_en_passant
                )
                if (
                    board.squares[end] != PIECE.INVALID
                    and board.squares[end] * board.turn <= 0
                    and ((not quiescent) or is_capture)  # quiescence check
                ):
                    yield Move(
                        start=start,
                        end=end,
                        moving_piece=type * board.turn,
                        is_capture=is_capture,
                        is_castle=False,
                        en_passant=-1,
                        is_king_capture=is_king_capture,
                    )
            # castling
            if (
                CASTLE.KING_SIDE * board.turn in board.castling_rights
                and board.squares[(96 if board.turn == COLOR.WHITE else 26)]
                == PIECE.EMPTY
                and board.squares[(97 if board.turn == COLOR.WHITE else 27)]
                == PIECE.EMPTY
            ):
                yield Move(
                    start=(95 if board.turn == COLOR.WHITE else 25),
                    end=(97 if board.turn == COLOR.WHITE else 27),
                    moving_piece=type * board.turn,
                    is_capture=False,
                    is_castle=True,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                )
            if (
                CASTLE.QUEEN_SIDE * board.turn in board.castling_rights
                and board.squares[(94 if board.turn == COLOR.WHITE else 24)]
                == PIECE.EMPTY
                and board.squares[(93 if board.turn == COLOR.WHITE else 23)]
                == PIECE.EMPTY
            ):
                yield Move(
                    start=(95 if board.turn == COLOR.WHITE else 25),
                    end=(93 if board.turn == COLOR.WHITE else 23),
                    moving_piece=type * board.turn,
                    is_capture=False,
                    is_castle=True,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                )
        if type == PIECE.PAWN:
            if not quiescent:
                depls = [(10 if board.turn == COLOR.BLACK else -10)]
                if start // 10 == (3 if board.turn == COLOR.BLACK else 8):
                    depls.append((20 if board.turn == COLOR.BLACK else -20))
                for depl in depls:
                    end = start + depl
                    if board.squares[end] == PIECE.EMPTY:
                        if abs(depl) == 20:
                            en_passant = start + depls[0]
                        else:
                            en_passant = -1
                        yield Move(
                            start=start,
                            end=end,
                            moving_piece=type * board.turn,
                            is_capture=False,
                            is_castle=False,
                            en_passant=en_passant,
                            is_king_capture=False,
                        )
                    else:
                        # do not allow 2 squares move if there's a piece in the way
                        break
            for depl in [9, 11] if board.turn == COLOR.BLACK else [-9, -11]:
                end = start + depl
                if (
                    board.squares[end] != PIECE.INVALID
                    and board.squares[end] * board.turn < 0
                    and (
                        (not quiescent) or end == board.king_en_passant
                    )  # quiescence check
                ) or end == board.en_passant:
                    is_king_capture = (
                        abs(board.squares[end]) == PIECE.KING or end == board.king_en_passant
                    )
                    yield Move(
                        start=start,
                        end=end,
                        moving_piece=type * board.turn,
                        is_capture=True,
                        is_castle=False,
                        en_passant=-1,
                        is_king_capture=is_king_capture,
                    )
