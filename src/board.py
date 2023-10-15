from dataclasses import dataclass
from functools import cache
from typing import Iterable

import evaluation
from constants import (
    ASCII_REP,
    CASTLE,
    COLOR,
    COLOR_DIRECTION,
    INV_COLOR,
    IS_PIECE,
    IS_PVALUE,
    PIECE,
    get_color,
)
from data_structures import Move


@dataclass(frozen=True)
class Board:
    # tuple of PIECE * COLOR
    # 120 squares for a 10*12 mailbox
    # https://www.chessprogramming.org/Mailbox
    squares: tuple[
        int,
        ...,
    ]
    # color of the player who's turn it is
    turn: COLOR
    # tuple reprensenting castling rights (index 2 * COLOR + CASTLE)
    castling_rights: tuple[
        int,
        ...,
    ]
    en_passant: int
    half_move: int
    full_move: int
    king_squares: tuple[
        int,
        ...,
    ]
    invturn: COLOR
    remaining_material: int
    hash_history: set[int]

    def __hash__(
        self,
    ) -> int:
        return hash(
            (
                self.squares,
                self.turn,
                self.castling_rights,
            )
        )

    def __str__(
        self,
    ) -> str:
        rep = f"{'w' if self.turn == COLOR.WHITE else 'b'}  0 1 2 3 4 5 6 7 8 9"
        for i in range(120):
            if i % 10 == 0:
                rep += f"\n{i//10:02d} "
            rep += f"{ASCII_REP[self.squares[i]]} "
        return rep


def _king_square(
    b: Board,
    color: COLOR,
) -> int | None:
    try:
        return int(b.squares.index(PIECE.KING + 6 * color))
    except Exception:
        return None


def _number_of(
    b: Board,
    piece: PIECE,
    color: COLOR,
) -> int:
    try:
        return int(b.squares.count(piece + 6 * color))
    except Exception:
        return 0


def _knight_moves(
    b: Board,
    start: int,
) -> Iterable[Move]:
    for depl in (
        21,
        12,
        -8,
        -19,
        -21,
        -12,
        8,
        19,
    ):
        end = start + depl
        is_capture = bool(b.squares[end])
        is_king_capture = IS_PIECE[b.squares[end]] == PIECE.KING
        if b.squares[end] != PIECE.INVALID and get_color(b.squares[end]) != b.turn:
            yield Move(
                start=start,
                end=end,
                moving_piece=PIECE.KNIGHT,
                captured_piece=IS_PIECE[b.squares[end]],
                is_capture=is_capture,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
            )


def _rook_moves(
    b: Board,
    start: int,
) -> Iterable[Move]:
    for direction in (
        10,
        -10,
        1,
        -1,
    ):
        for x in range(
            1,
            8,
        ):
            end = start + x * direction
            is_capture = bool(b.squares[end])
            is_king_capture = IS_PIECE[b.squares[end]] == PIECE.KING

            # castling moves are processed here
            # because we are already checking if the path is clear that way
            if (
                b.castling_rights[2 * b.turn + CASTLE.KING_SIDE] == 1
                and start == (28 if b.turn == COLOR.BLACK else 98)
                and IS_PIECE[b.squares[end]] == PIECE.KING
                and get_color(b.squares[end]) == b.turn
                and not king_is_in_check(
                    b,
                    b.turn,
                )
            ):
                yield Move(
                    start=(95 if b.turn == COLOR.WHITE else 25),
                    end=(97 if b.turn == COLOR.WHITE else 27),
                    moving_piece=PIECE.KING,
                    captured_piece=PIECE.EMPTY,
                    is_capture=False,
                    is_castle=True,
                    en_passant=-1,
                    is_king_capture=False,
                )
            if (
                b.castling_rights[2 * b.turn + CASTLE.QUEEN_SIDE] == 1
                and start == (21 if b.turn == COLOR.BLACK else 91)
                and IS_PIECE[b.squares[end]] == PIECE.KING
                and get_color(b.squares[end]) == b.turn
                and not king_is_in_check(
                    b,
                    b.turn,
                )
            ):
                yield Move(
                    start=(95 if b.turn == COLOR.WHITE else 25),
                    end=(93 if b.turn == COLOR.WHITE else 23),
                    moving_piece=PIECE.KING,
                    captured_piece=PIECE.EMPTY,
                    is_capture=False,
                    is_castle=True,
                    en_passant=-1,
                    is_king_capture=False,
                )

            if b.squares[end] != PIECE.INVALID and get_color(b.squares[end]) != b.turn:
                yield Move(
                    start=start,
                    end=end,
                    moving_piece=PIECE.ROOK,
                    captured_piece=IS_PIECE[b.squares[end]],
                    is_capture=is_capture,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                )
            if b.squares[end] != PIECE.EMPTY or is_capture:
                break


def _bishop_moves(
    b: Board,
    start: int,
) -> Iterable[Move]:
    for direction in (
        11,
        -11,
        9,
        -9,
    ):
        for x in range(
            1,
            8,
        ):
            end = start + x * direction
            is_capture = bool(b.squares[end])
            is_king_capture = IS_PIECE[b.squares[end]] == PIECE.KING
            if b.squares[end] != PIECE.INVALID and get_color(b.squares[end]) != b.turn:
                yield Move(
                    start=start,
                    end=end,
                    moving_piece=PIECE.BISHOP,
                    captured_piece=IS_PIECE[b.squares[end]],
                    is_capture=is_capture,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                )
            if b.squares[end] != PIECE.EMPTY or is_capture:
                break


def _queen_moves(
    b: Board,
    start: int,
) -> Iterable[Move]:
    for direction in (
        11,
        -11,
        9,
        -9,
        10,
        -10,
        1,
        -1,
    ):
        for x in range(
            1,
            8,
        ):
            end = start + x * direction
            is_capture = bool(b.squares[end])
            is_king_capture = IS_PIECE[b.squares[end]] == PIECE.KING
            if b.squares[end] != PIECE.INVALID and get_color(b.squares[end]) != b.turn:
                yield Move(
                    start=start,
                    end=end,
                    moving_piece=PIECE.QUEEN,
                    captured_piece=IS_PIECE[b.squares[end]],
                    is_capture=is_capture,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                )
            if b.squares[end] != PIECE.EMPTY or is_capture:
                break


def _king_moves(
    b: Board,
    start: int,
) -> Iterable[Move]:
    for depl in (
        11,
        -11,
        9,
        -9,
        1,
        -1,
        10,
        -10,
    ):
        end = start + depl
        is_capture = bool(b.squares[end])
        is_king_capture = IS_PIECE[b.squares[end]] == PIECE.KING
        if b.squares[end] != PIECE.INVALID and get_color(b.squares[end]) != b.turn:
            yield Move(
                start=start,
                end=end,
                moving_piece=PIECE.KING,
                captured_piece=IS_PIECE[b.squares[end]],
                is_capture=is_capture,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
            )


def _pawn_moves(
    b: Board,
    start: int,
) -> Iterable[Move]:
    if b.turn == COLOR.BLACK:
        if start < 40:
            depls: tuple[int] | tuple[
                int,
                int,
            ] = (
                10,
                20,
            )
        else:
            depls = (10,)
    else:
        if start > 79:
            depls = (-10, -20)
        else:
            depls = (-10,)
    for depl in depls:
        end = start + depl
        if b.squares[end] == PIECE.EMPTY:
            if depl in (
                -20,
                20,
            ):
                en_passant = start + depls[0]
            else:
                en_passant = -1
            yield Move(
                start=start,
                end=end,
                moving_piece=PIECE.PAWN,
                captured_piece=PIECE.EMPTY,
                is_capture=False,
                is_castle=False,
                en_passant=en_passant,
                is_king_capture=False,
            )
        else:
            # do not allow 2 squares move if there's a piece in the way
            break
    for depl in (9, 11) if b.turn == COLOR.BLACK else (-9, -11):
        end = start + depl
        if (
            b.squares[end] not in (PIECE.EMPTY, PIECE.INVALID)
            and get_color(b.squares[end]) != b.turn
        ) or end == b.en_passant:
            is_king_capture = IS_PIECE[b.squares[end]] == PIECE.KING
            yield Move(
                start=start,
                end=end,
                moving_piece=PIECE.PAWN,
                captured_piece=IS_PIECE[b.squares[end]] if end != b.en_passant else PIECE.PAWN,
                is_capture=True,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
            )


def _is_legal_move(
    b: Board,
    move: Move,
) -> bool:
    if not is_pseudo_legal_move(b, move):
        return False

    # verify that the king of the player to move exists
    if (_number_of(b, PIECE.KING, b.turn) < 1):
        return False

    b2 = push(b, move)

    # the king should not be in check after the move
    ks = _king_square(b2, b2.invturn)
    if ks is None:
        return False

    if is_square_attacked(b2.squares, ks, b2.turn):
        return False

    ks = _king_square(b, b.turn)
    if ks is None:
        return False

    # a castling move is only acceptable if the king is not in check
    if move.is_castle and is_square_attacked(b.squares, ks, b.invturn):
        return False

    # a castling move is not acceptable if some transition squares are attacked
    if move.is_castle:
        if move.end > move.start and is_square_attacked(
            b.squares,
            move.start + 1,
            b.invturn,
        ):
            return False
        if move.end < move.start and is_square_attacked(
            b.squares,
            move.start - 1,
            b.invturn,
        ):
            return False

    return True


def push(
    b: Board,
    move: Move,
    fast: bool = True,
) -> Board:
    squares = list(b.squares)
    en_passant = -1
    castling_rights = list(b.castling_rights)
    half_move = b.half_move + 1
    king_squares = list(b.king_squares)
    full_move = b.full_move + 1 if b.turn == COLOR.BLACK else b.full_move
    remaining_material = b.remaining_material

    if not fast:
        hash_history = b.hash_history.copy()
        hash_history.add(hash(b))
    else:
        hash_history = b.hash_history

    assert b.squares[move.start] != PIECE.EMPTY, "Moving piece cannot be empty"
    assert IS_PIECE[b.squares[move.start]] != PIECE.INVALID, "Moving piece cannot be invalid"

    piece_start = b.squares[move.start]

    if (
        move.is_capture
        and move.captured_piece != PIECE.INVALID
        and move.captured_piece != PIECE.EMPTY
    ):
        remaining_material -= evaluation.PIECE_VALUE[move.captured_piece]

    if move.is_capture or IS_PIECE[piece_start] == PIECE.PAWN:
        # reset half_move count when condition is met
        half_move = 0

    # do the move
    squares[move.start] = PIECE.EMPTY
    squares[move.end] = piece_start

    # change the king square
    if IS_PIECE[piece_start] == PIECE.KING:
        king_squares[b.turn] = move.end

    # special removal for "en passant" moves
    if move.end == b.en_passant and IS_PIECE[piece_start] == PIECE.PAWN:
        target = move.end + (10 * COLOR_DIRECTION[b.turn])
        squares[target] = PIECE.EMPTY

    # declare en_passant square for the current board
    if move.en_passant != -1:
        en_passant = move.en_passant
    else:
        en_passant = -1

    # promotion
    if IS_PIECE[piece_start] == PIECE.PAWN and move.end // 10 == (
        2 if b.turn == COLOR.WHITE else 9
    ):
        squares[move.end] = IS_PVALUE[
            (
                b.turn,
                PIECE.QUEEN,
            )
        ]

    # some hardcode for castling move of the rook
    if move.is_castle:
        castling_rights[2 * b.turn + CASTLE.KING_SIDE] = 0
        castling_rights[2 * b.turn + CASTLE.QUEEN_SIDE] = 0
        if move.end == 97:
            squares[98] = PIECE.EMPTY
            squares[95] = PIECE.EMPTY
            squares[96] = IS_PVALUE[
                (
                    COLOR.WHITE,
                    PIECE.ROOK,
                )
            ]
        if move.end == 93:
            squares[91] = PIECE.EMPTY
            squares[95] = PIECE.EMPTY
            squares[94] = IS_PVALUE[
                (
                    COLOR.WHITE,
                    PIECE.ROOK,
                )
            ]
        if move.end == 27:
            squares[28] = PIECE.EMPTY
            squares[25] = PIECE.EMPTY
            squares[26] = IS_PVALUE[
                (
                    COLOR.BLACK,
                    PIECE.ROOK,
                )
            ]
        if move.end == 23:
            squares[21] = PIECE.EMPTY
            squares[25] = PIECE.EMPTY
            squares[24] = IS_PVALUE[
                (
                    COLOR.BLACK,
                    PIECE.ROOK,
                )
            ]
    else:
        # remove castling rights
        if IS_PIECE[piece_start] == PIECE.KING:
            castling_rights[2 * b.turn + CASTLE.KING_SIDE] = 0
            castling_rights[2 * b.turn + CASTLE.QUEEN_SIDE] = 0
        else:
            if move.end == 98 or move.start == 98:
                castling_rights[2 * COLOR.WHITE + CASTLE.KING_SIDE] = 0
            if move.end == 91 or move.start == 91:
                castling_rights[2 * COLOR.WHITE + CASTLE.QUEEN_SIDE] = 0
            if move.end == 28 or move.start == 28:
                castling_rights[2 * COLOR.BLACK + CASTLE.KING_SIDE] = 0
            if move.end == 21 or move.start == 21:
                castling_rights[2 * COLOR.BLACK + CASTLE.QUEEN_SIDE] = 0

    # check that border squares are still invalid
    assert not any(
        filter(
            lambda x: x != PIECE.INVALID,
            squares[:20],
        )
    )
    assert not any(
        filter(
            lambda x: x != PIECE.INVALID,
            squares[100:],
        )
    )
    assert not any(
        filter(
            lambda x: x != PIECE.INVALID,
            [v for k, v in enumerate(squares) if k % 10 == 0],
        )
    )
    assert not any(
        filter(
            lambda x: x != PIECE.INVALID,
            [v for k, v in enumerate(squares) if k % 10 == 9],
        )
    )

    return Board(
        tuple(squares),
        COLOR(INV_COLOR[b.turn]),
        tuple(castling_rights),
        en_passant,
        half_move,
        full_move,
        tuple(king_squares),
        COLOR(INV_COLOR[b.invturn]),
        remaining_material,
        hash_history=hash_history,
    )


# Some fast verifications to check if a move is pseudo legal
def is_pseudo_legal_move(
    b: Board,
    move: Move,
) -> bool:
    if move.start < 21 or move.start > 98:
        return False
    if move.end < 21 or move.end > 98:
        return False
    if IS_PIECE[b.squares[move.start]] != move.moving_piece:
        return False
    if move.is_capture:
        if b.squares[move.end] == PIECE.EMPTY and move.end != b.en_passant:
            return False
        if move.captured_piece != (
            IS_PIECE[b.squares[move.end]] if move.end != b.en_passant else PIECE.PAWN
        ):
            return False
    if not move.is_capture:
        if b.squares[move.end] != PIECE.EMPTY:
            return False
    return True


def legal_moves(
    b: Board,
) -> list[Move]:
    moves = []

    if _number_of(b, PIECE.KING, b.turn) < 1:
        return []

    for move in pseudo_legal_moves(b):
        if not _is_legal_move(
            b,
            move,
        ):
            continue
        moves.append(move)
    return moves


@cache
def is_square_attacked(
    squares: tuple[int, ...],
    square: int,
    color: COLOR,
) -> bool:
    """Detect if square on b is attacked by color."""
    for depl in (21, 12, -8, -19, -21, -12, 8, 19):
        if squares[square + depl] == PIECE.KNIGHT + 6 * color:
            return True

    for direction in (1, -1, 10, -10):
        for x in range(1, 8):
            end = square + x * direction
            if (
                squares[end] == PIECE.ROOK + 6 * color
                or squares[end] == PIECE.QUEEN + 6 * color
                or (x == 1 and squares[end] == PIECE.KING + 6 * color)
            ):
                return True
            if squares[end] != PIECE.EMPTY:
                break

    for direction in (11, -11, 9, -9):
        for x in range(1, 8):
            end = square + x * direction
            if (
                squares[end] == PIECE.BISHOP + 6 * color
                or squares[end] == PIECE.QUEEN + 6 * color
                or (x == 1 and squares[end] == PIECE.KING + 6 * color)
            ):
                return True
            if squares[end] != PIECE.EMPTY:
                break

    for depl in (9, 11) if color == COLOR.WHITE else (-9, -11):
        if squares[square + depl] == PIECE.PAWN + 6 * color:
            return True
    return False


def king_is_in_check(
    b: Board,
    color: COLOR,
) -> bool:
    if is_square_attacked(
        b.squares,
        b.king_squares[color],
        INV_COLOR[color],
    ):
        return True
    return False


# Special function to create moves that target a square
# Useful for the SEE function
# is LVA (least valuable attacker) by implementation
def capture_moves(
    b: Board,
    target: int,
) -> Iterable[Move]:
    is_king_capture = IS_PIECE[b.squares[target]] == PIECE.KING

    # PAWN
    for depl in (
        (
            9,
            11,
        )
        if b.turn == COLOR.WHITE
        else (
            -9,
            -11,
        )
    ):
        start = target + depl
        if IS_PIECE[b.squares[start]] == PIECE.PAWN and get_color(b.squares[start]) == b.turn:
            yield Move(
                start=start,
                end=target,
                moving_piece=PIECE.PAWN,
                captured_piece=IS_PIECE[b.squares[target]],
                is_capture=True,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
            )

    # KNIGHT
    for depl in (21, 12, -8, -19, -21, -12, 8, 19):
        start = target + depl
        if IS_PIECE[b.squares[start]] == PIECE.KNIGHT and get_color(b.squares[start]) == b.turn:
            yield Move(
                start=start,
                end=target,
                moving_piece=PIECE.KNIGHT,
                captured_piece=IS_PIECE[b.squares[target]],
                is_capture=True,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
            )

    # BISHOP
    for direction in (11, -11, 9, -9):
        for x in range(1, 8):
            start = target + x * direction

            if (
                IS_PIECE[b.squares[start]] == PIECE.BISHOP
                and get_color(b.squares[start]) == b.turn
            ):
                yield Move(
                    start=start,
                    end=target,
                    moving_piece=IS_PIECE[b.squares[start]],
                    captured_piece=IS_PIECE[b.squares[target]],
                    is_capture=True,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                )
            if b.squares[start] != PIECE.EMPTY:
                break

    # ROOK
    for direction in (1, -1, 10, -10):
        for x in range(1, 8):
            start = target + x * direction

            if IS_PIECE[b.squares[start]] == PIECE.ROOK and get_color(b.squares[start]) == b.turn:
                yield Move(
                    start=start,
                    end=target,
                    moving_piece=IS_PIECE[b.squares[start]],
                    captured_piece=IS_PIECE[b.squares[target]],
                    is_capture=True,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                )
            if b.squares[start] != PIECE.EMPTY:
                break

    # QUEEN
    for direction in (11, -11, 9, -9, 10, -10, 1, -1):
        for x in range(1, 8):
            start = target + x * direction

            if IS_PIECE[b.squares[start]] == PIECE.QUEEN and get_color(b.squares[start]) == b.turn:
                yield Move(
                    start=start,
                    end=target,
                    moving_piece=PIECE.QUEEN,
                    captured_piece=IS_PIECE[b.squares[target]],
                    is_capture=True,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=is_king_capture,
                )
            if b.squares[start] != PIECE.EMPTY:
                break

    # KING
    for depl in (11, -11, 9, -9, 1, -1, 10, -10):
        start = target + depl
        if IS_PIECE[b.squares[start]] == PIECE.KING and get_color(b.squares[start]) == b.turn:
            yield Move(
                start=start,
                end=target,
                moving_piece=PIECE.KING,
                captured_piece=IS_PIECE[b.squares[target]],
                is_capture=True,
                is_castle=False,
                en_passant=-1,
                is_king_capture=is_king_capture,
            )


def pseudo_legal_moves(
    b: Board,
) -> Iterable[Move]:
    for i in range(8):
        for j in range(8):
            start = (2 + j) * 10 + (i + 1)
            piece = b.squares[start]
            if get_color(piece) != b.turn:
                continue
            piece_type = IS_PIECE[piece]
            if piece_type == PIECE.PAWN:
                yield from _pawn_moves(b, start)
                continue
            if piece_type == PIECE.KNIGHT:
                yield from _knight_moves(b, start)
                continue
            if piece_type == PIECE.BISHOP:
                yield from _bishop_moves(b, start)
                continue
            if piece_type == PIECE.ROOK:
                yield from _rook_moves(b, start)
                continue
            if piece_type == PIECE.QUEEN:
                yield from _queen_moves(b, start)
                continue
            if piece_type == PIECE.KING:
                yield from _king_moves(b, start)
                continue


# Should return capture moves in MVV-LVA order
# Should end with check moves (and promotions ?)
def tactical_moves(
    b: Board,
) -> Iterable[Move]:
    """Generate only tactical moves.

    First we generate capture moves.
    These capture moves should be generated in a manner
    that respects MVV-LVA (so that we don't have to do some move ordering later).

    First we need to have the position of ennemy pieces.
    We don't store the position of the enemy queens since their captures are
    evaluated immediately (this saves a list generation
    """
    piece_pawn = []
    piece_knight = []
    piece_bishop = []
    piece_rook = []

    for i in range(8):
        for j in range(8):
            square = (2 + j) * 10 + (i + 1)
            piece = b.squares[square]
            color = get_color(piece)
            if color != b.invturn:
                continue
            if IS_PIECE[piece] == PIECE.PAWN:
                piece_pawn.append(square)
                continue
            if IS_PIECE[piece] == PIECE.KNIGHT:
                piece_knight.append(square)
                continue
            if IS_PIECE[piece] == PIECE.BISHOP:
                piece_bishop.append(square)
                continue
            if IS_PIECE[piece] == PIECE.ROOK:
                piece_rook.append(square)
                continue
            if IS_PIECE[piece] == PIECE.QUEEN:
                yield from capture_moves(
                    b,
                    square,
                )
                continue

    # We assume that we cannot take the enemy king.
    # The captures against the enemy queens were already yielded.
    # So we start by yielding captures against the enemy rooks, and then bishop...
    for square in piece_rook:
        yield from capture_moves(b, square)
    for square in piece_bishop:
        yield from capture_moves(
            b,
            square,
        )
    for square in piece_knight:
        yield from capture_moves(
            b,
            square,
        )
    for square in piece_pawn:
        yield from capture_moves(
            b,
            square,
        )

    # handle en passant
    if b.en_passant != -1:
        for depl in (
            (
                9,
                11,
            )
            if b.turn == COLOR.WHITE
            else (
                -9,
                -11,
            )
        ):
            start = b.en_passant + depl
            if IS_PIECE[b.squares[start]] == PIECE.PAWN and get_color(b.squares[start]) == b.turn:
                yield Move(
                    start=start,
                    end=b.en_passant,
                    moving_piece=PIECE.PAWN,
                    captured_piece=IS_PIECE[b.squares[b.en_passant]],
                    is_capture=True,
                    is_castle=False,
                    en_passant=-1,
                    is_king_capture=False,
                )
