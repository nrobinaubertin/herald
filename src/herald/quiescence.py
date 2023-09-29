from . import board, evaluation, pruning
from .board import Board
from .configuration import Config
from .constants import COLOR, COLOR_DIRECTION, PIECE, VALUE_MAX


def quiescence(
    *,
    config: Config,
    b: Board,
    depth: int = 0,
    alpha: int,
    beta: int,
) -> int:
    assert depth >= 0, depth

    # if we are on a terminal node, return the evaluation
    if depth >= config.quiescence_depth:
        return evaluation.evaluation(
            b.squares,
            b.remaining_material,
        )

    we_are_in_check = board.is_square_attacked(
        b.squares,
        b.king_squares[b.turn],
        b.invturn,
    )

    if not we_are_in_check:
        # stand_pat evaluation to check if we stop QS
        stand_pat: int = evaluation.evaluation(
            b.squares,
            b.remaining_material,
        )
        # if depth == 0:
        #     print(stand_pat)
        if b.turn == COLOR.WHITE:
            if stand_pat >= beta:
                return beta
            # delta pruning
            if stand_pat + evaluation.PIECE_VALUE[PIECE.QUEEN] < alpha:
                return alpha
            alpha = max(alpha, stand_pat)
        else:
            if stand_pat <= alpha:
                return alpha
            # delta pruning
            if stand_pat - evaluation.PIECE_VALUE[PIECE.QUEEN] > beta:
                return beta
            beta = min(beta, stand_pat)
        best = stand_pat
        moves = board.tactical_moves(b)
    else:
        best = None
        moves = board.pseudo_legal_moves(b)

    for move in moves:
        if not we_are_in_check:
            # if we are not evaluating a capture move
            # and if we found already something good
            # then we can skip the rest
            # (capture moves are generated first)
            if not move.is_capture and best is not None:
                break

            # skip bad capture moves
            if pruning.is_bad_capture(b, move):
                continue

        nb = board.push(b, move)

        # if the king is in check after we move
        # then it's a bad move (we will lose the game)
        if board.king_is_in_check(nb, nb.invturn):
            continue

        value = quiescence(
            config=config,
            b=nb,
            depth=depth + 1,
            alpha=alpha,
            beta=beta,
        )

        if b.turn == COLOR.WHITE:
            if best is None or value > best:
                best = value
            alpha = max(alpha, value)
            if value >= beta:
                break
        else:
            if best is None or value < best:
                best = value
            beta = min(beta, value)
            if value <= alpha:
                break

    if best is not None:
        return best
    else:
        # this happens when no quiescent move is available
        # if the king square is attacked and we have no moves, it's a mate
        if board.is_square_attacked(
            b.squares,
            b.king_squares[b.turn],
            b.invturn,
        ):
            return VALUE_MAX * COLOR_DIRECTION[b.turn] * -1
        else:
            return evaluation.evaluation(
                b.squares,
                b.remaining_material,
            )
