import chess
import constants

class Board():

    def __init__(self, fen = constants.STARTPOS, board = None):
        if board is None:
            self.board = chess.Board(fen)
        else:
            self.board = board

    def pieces(self, type: constants.PIECE, color: constants.COLOR):
        return self.board.pieces(self.convert_type(type), self.convert_color(color))

    def piece_at(self, square: constants.SQUARE) -> constants.PIECE:
        return self.convert_type(self.board.piece_at(square), True)

    def is_quiescent_move(self, move) -> bool:
        return self.board.is_capture(move)

    def is_valid(self):
        return self.board.is_valid()

    def king(self, color: constants.COLOR):
        return self.board.king(self.convert_color(color))

    def invert_color(self, color: constants.COLOR) -> constants.COLOR:
        return constants.COLOR.WHITE if color == constants.COLOR.BLACK else constants.COLOR.BLACK

    def fen(self):
        return self.board.fen()

    @property
    def turn(self) -> constants.COLOR:
        return self.convert_color(self.board.turn, invert=True)

    def push(self, move):
        self.board.push(move)

    def copy(self):
        return Board(board=self.board.copy())

    def moves(self, quiescent: bool = False):
        if quiescent:
            return filter(self.is_quiescent_move, self.board.legal_moves)
        return self.board.legal_moves

    def is_game_over(self) -> bool:
        return self.board.is_game_over()

    def outcome(self):
        return self.board.outcome()

    def debug_move_stack(self):
        return [x.uci() for x in self.board.move_stack]

    def convert_color(self, color, invert: bool = False):
        if not invert:
            if color == constants.COLOR.WHITE:
                return chess.WHITE
            if color == constants.COLOR.BLACK:
                return chess.BLACK
        else:
            if color == chess.WHITE:
                return constants.COLOR.WHITE
            if color == chess.BLACK:
                return constants.COLOR.BLACK
        raise Exception("Unknown color!")

    def convert_type(self, type, invert: bool = False):
        if not invert:
            if type == constants.PIECE.PAWN:
                return chess.PAWN
            if type == constants.PIECE.KNIGHT:
                return chess.KNIGHT
            if type == constants.PIECE.BISHOP:
                return chess.BISHOP
            if type == constants.PIECE.ROOK:
                return chess.ROOK
            if type == constants.PIECE.QUEEN:
                return chess.QUEEN
            if type == constants.PIECE.KING:
                return chess.KING
        else:
            if type == chess.PAWN:
                return constants.PIECE.PAWN
            if type == chess.KNIGHT:
                return constants.PIECE.KNIGHT
            if type == chess.BISHOP:
                return constants.PIECE.BISHOP
            if type == chess.ROOK:
                return constants.PIECE.ROOK
            if type == chess.QUEEN:
                return constants.PIECE.QUEEN
            if type == chess.KING:
                return constants.PIECE.KING
        raise Exception("Unknown type!")

    def __str__(self):
        return str(self.board)
