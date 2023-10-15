import board
import evaluation
from constants import (
    ASCII_REP,
    CASTLE,
    COLOR,
    IS_PIECE,
    PIECE,
)
from data_structures import Move
from typing import Iterable


def decompose_square(
    square: int,
) -> tuple[int, int,]:
    row = 10 - (square // 10 - 2) - 2
    column = square - (square // 10) * 10
    return (row, column)


def is_promotion(move: Move) -> bool:
    (
        row,
        _,
    ) = decompose_square(move.end)
    return move.moving_piece == PIECE.PAWN and row in (8, 1)


def to_normal_notation(square: int) -> str:
    (row, column) = decompose_square(square)
    letter = (
        {
            1: "a",
            2: "b",
            3: "c",
            4: "d",
            5: "e",
            6: "f",
            7: "g",
            8: "h",
        }
    )[column]
    return f"{letter}{row}"


def to_square_notation(uci: str) -> int:
    uci = uci.lower()
    digits = {
        "a": 1,
        "b": 2,
        "c": 3,
        "d": 4,
        "e": 5,
        "f": 6,
        "g": 7,
        "h": 8,
    }
    return digits[uci[0]] + (10 - int(uci[1])) * 10


def from_uci(b: board.Board, uci: str) -> Move:
    start = to_square_notation(uci[:2])
    end = to_square_notation(uci[2:])
    is_capture = IS_PIECE[b.squares[end]] != PIECE.EMPTY or end == b.en_passant
    return Move(
        start=start,
        end=end,
        moving_piece=IS_PIECE[b.squares[start]],
        is_capture=is_capture,
        captured_piece=(
            PIECE.EMPTY
            if not is_capture
            else IS_PIECE[b.squares[end]]
            if end != b.en_passant
            else PIECE.PAWN
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


def to_uci(input_move: Move | Iterable[Move]) -> str:
    if isinstance(input_move, Move):
        return (
            f"{to_normal_notation(input_move.start)}"
            f"{to_normal_notation(input_move.end)}"
            f"{'q' if is_promotion(input_move) else ''}"
        )

    if isinstance(input_move, Iterable):
        return " ".join([to_uci(x) for x in input_move])

    raise Exception("Unknown input_move for to_uci()")


def to_fen(b: board.Board) -> str:
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
    if b.castling_rights[2 * COLOR.WHITE + CASTLE.KING_SIDE] == 1:
        rep += "K"
    if b.castling_rights[2 * COLOR.WHITE + CASTLE.QUEEN_SIDE] == 1:
        rep += "Q"
    if b.castling_rights[2 * COLOR.BLACK + CASTLE.KING_SIDE] == 1:
        rep += "k"
    if b.castling_rights[2 * COLOR.BLACK + CASTLE.QUEEN_SIDE] == 1:
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


def from_fen(fen: str) -> board.Board:
    if fen == "startpos":
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    (
        rep,
        turn,
        castling_rights,
        en_passant,
        half_move,
        full_move,
    ) = fen.split()

    cr = (
        1 if "K" in castling_rights else 0,
        1 if "Q" in castling_rights else 0,
        1 if "k" in castling_rights else 0,
        1 if "q" in castling_rights else 0,
    )

    squares = [int(PIECE.INVALID)] * 120
    ks: list[int] = [0, 0]
    s = 19
    for row in rep.split("/"):
        squares[(s := s + 1)] = PIECE.INVALID
        for c in row:
            piece = None
            color = COLOR.BLACK if c.islower() else COLOR.WHITE
            if c.lower() == "r":
                piece = PIECE.ROOK + 6 * color
            if c.lower() == "n":
                piece = PIECE.KNIGHT + 6 * color
            if c.lower() == "b":
                piece = PIECE.BISHOP + 6 * color
            if c.lower() == "q":
                piece = PIECE.QUEEN + 6 * color
            if c.lower() == "k":
                piece = PIECE.KING + 6 * color
                ks[color] = s + 1
            if c.lower() == "p":
                piece = PIECE.PAWN + 6 * color
            if piece is not None:
                squares[(s := s + 1)] = piece
            elif int(c) > 0:
                for _ in range(int(c)):
                    squares[(s := s + 1)] = PIECE.EMPTY
        squares[(s := s + 1)] = PIECE.INVALID

    # this conversion is done for type safety purposes
    king_squares: tuple[int, int] = (ks[0], ks[1])

    b = board.Board(
        tuple(squares),
        COLOR.WHITE if turn == "w" else COLOR.BLACK,
        cr,
        (to_square_notation(en_passant) if en_passant != "-" else -1),
        int(half_move),
        int(full_move),
        king_squares,
        COLOR.WHITE if turn == "b" else COLOR.BLACK,
        evaluation.remaining_material(tuple(squares)),
        set(),
    )

    return b
