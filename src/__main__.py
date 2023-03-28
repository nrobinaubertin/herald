#!/usr/bin/env -S python3 -O
import multiprocessing
import sys
import threading

from herald import algorithms, board, evaluation, move_ordering, pruning, quiescence
from herald.board import Board
from herald.configuration import Config
from herald.constants import COLOR, VALUE_MAX
from herald.data_structures import to_uci
from herald.iterative_deepening import itdep
from herald.pruning import see
from herald.time_management import target_movetime

CURRENT_BOARD = board.from_fen("startpos")
CURRENT_PROCESS = None
CURRENT_QUEUE = None
LAST_SEARCH = None

CONFIG = Config(
    alg_fn=algorithms.alphabeta,
    move_ordering_fn=move_ordering.fast_ordering,
    quiescence_search=True,
    quiescence_depth=9,
    use_transposition_table=True,
    use_hash_move=True,
    use_killer_moves=True,
    use_late_move_reduction=False,
    use_saved_search=True,
    quiescence_fn=quiescence.quiescence,
)


def stop_calculating() -> None:
    global CURRENT_PROCESS
    global CURRENT_QUEUE
    if CURRENT_PROCESS is not None:
        CURRENT_PROCESS.terminate()
    CURRENT_QUEUE = None


def uci_parser(line: str) -> list[str]:  # noqa: C901
    global CURRENT_BOARD
    global CURRENT_PROCESS
    global CURRENT_QUEUE
    global LAST_SEARCH
    tokens = line.strip().split()

    if not tokens:
        return []

    if tokens[0] == "checks":
        return [
            f"White king is in check: {board.king_is_in_check(CURRENT_BOARD, COLOR.WHITE)}",
            f"Black king is in check: {board.king_is_in_check(CURRENT_BOARD, COLOR.BLACK)}",
        ]

    if tokens[0] == "lastsearch":
        if LAST_SEARCH is not None:
            return [f"LAST SEARCH: {to_uci(LAST_SEARCH.pv)}"]
        else:
            return ["LAST SEARCH: None"]

    if tokens[0] == "see":
        return [f"SEE: {see(CURRENT_BOARD, int(tokens[1]), 0)}"]

    if tokens[0] == "eval":
        return [
            f"board: {evaluation.eval_fast(CURRENT_BOARD.squares, evaluation.remaining_material(CURRENT_BOARD.squares))}"
        ]

    if tokens[0] == "remaining_material":
        return [f"board: {CURRENT_BOARD.remaining_material}"]

    if tokens[0] == "print":
        return [board.to_string(CURRENT_BOARD)]

    if tokens[0] == "quietlines":
        moves = (move for move in board.tactical_moves(CURRENT_BOARD))
        moves = (move for move in moves if not pruning.is_bad_capture(CURRENT_BOARD, move))
        for move in moves:
            nb = board.push(CURRENT_BOARD, move, fast=False)
            node = quiescence.quiescence(CONFIG, nb, [move], -VALUE_MAX, VALUE_MAX, True)
            print([node.value] + [to_uci(m) for m in node.pv])

    if tokens[0] == "lines":
        moves = (move for move in board.legal_moves(CURRENT_BOARD))
        for move in moves:
            nb = board.push(CURRENT_BOARD, move, fast=False)
            for node in algorithms.alphabeta(
                config=CONFIG,
                b=nb,
                depth=int(tokens[1]),
                pv=[move]
            ):
                continue
            print([node.value] + [to_uci(m) for m in node.pv])

    if tokens[0] == "quiescence":
        if CURRENT_PROCESS is not None:
            CURRENT_PROCESS.terminate()

        process = multiprocessing.Process(
            target=quiescence.quiescence,
            args=(CONFIG, CURRENT_BOARD, [], -VALUE_MAX, VALUE_MAX, True),
            daemon=False,
        )
        process.start()
        CURRENT_PROCESS = process

    if tokens[0] == "quietmoves":
        moves = (move for move in board.tactical_moves(CURRENT_BOARD))
        moves = (move for move in moves if not pruning.is_bad_capture(CURRENT_BOARD, move))
        return [", ".join([to_uci(m) for m in moves])]

    if tokens[0] == "pseudomoves":
        return [", ".join([to_uci(m) for m in board.pseudo_legal_moves(CURRENT_BOARD)])]

    if tokens[0] == "tacticalmoves":
        return [", ".join([to_uci(m) for m in board.tactical_moves(CURRENT_BOARD)])]

    if tokens[0] == "captures":
        return [", ".join([to_uci(m) for m in board.capture_moves(CURRENT_BOARD, int(tokens[1]))])]

    if tokens[0] == "moves":
        return [", ".join([to_uci(m) for m in board.legal_moves(CURRENT_BOARD)])]

    if tokens[0] == "fen":
        return [board.to_fen(CURRENT_BOARD)]

    if tokens[0] == "perft":
        total = 0
        to_display = []

        def execute(b: Board, depth: int) -> int:
            if depth == 0:
                return 1

            if depth == 1:
                return len(list(board.legal_moves(b)))

            nodes = 0
            for move in board.legal_moves(b):
                curr_board = board.push(b, move)
                nodes += execute(curr_board, depth - 1)

            return nodes

        for move in board.legal_moves(CURRENT_BOARD):
            b = board.push(CURRENT_BOARD, move)
            nodes = execute(b, int(tokens[1]) - 1)
            to_display.append(f"{to_uci(move)}: {nodes}")
            total += nodes
        to_display.append(f"Nodes: {total}")
        return to_display

    if len(tokens) == 1 and tokens[0] == "uci":
        return [
            f"{CONFIG.name} {CONFIG.version} by {CONFIG.author}",
            f"id name {CONFIG.name}",
            f"id author {CONFIG.author}",
            # fake some options
            "option name Hash type spin default 16 min 1 max 33554432",
            "option name Move Overhead type spin default 10 min 0 max 5000",
            "option name Threads type spin default 1 min 1 max 1",
            "uciok",
        ]

    if tokens[0] == "clearsearch":
        LAST_SEARCH = None

    if tokens[0] == "stop":
        stop_calculating()

    if tokens[0] == "quit":
        stop_calculating()
        sys.exit()

    if tokens[0] == "play":
        move = board.from_uci(CURRENT_BOARD, tokens[1])
        CURRENT_BOARD = board.push(CURRENT_BOARD, move, fast=False)

    if tokens[0] == "ucinewgame":
        CURRENT_BOARD = board.from_fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
        return []

    if tokens[0] == "isready":
        return [
            "readyok",
        ]

    if len(tokens) > 1 and tokens[0] == "position":
        next_token = 1
        if tokens[next_token] == "fen":
            next_token += 1
        if tokens[next_token] == "startpos":
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            next_token += 1
        else:
            fen = (
                f"{tokens[next_token]} "
                f"{tokens[next_token + 1]} {tokens[next_token + 2]} {tokens[next_token + 3]} "
                f"{tokens[next_token + 4] if len(tokens) > next_token + 4 else 0} "
                f"{tokens[next_token + 5] if len(tokens) > next_token + 5 else 0}"
            )
            next_token += 6
        b = board.from_fen(fen)
        if len(tokens) > next_token and tokens[next_token] == "moves":
            for move_str in tokens[next_token + 1 :]:
                b = board.push(b, board.from_uci(b, move_str), fast=False)
        CURRENT_BOARD = b

    if len(tokens) > 1 and tokens[0] == "go":
        depth = 0
        movetime = 0
        wtime = 0
        btime = 0
        winc = 0
        binc = 0

        if tokens[1] == "movetime":
            movetime = int(tokens[2])

        if len(tokens) > 8:
            if tokens[1] == "wtime":
                wtime = int(tokens[2])
            if tokens[3] == "btime":
                btime = int(tokens[4])
            if tokens[5] == "winc":
                winc = int(tokens[6])
            if tokens[7] == "binc":
                binc = int(tokens[8])

        if tokens[1] == "depth":
            depth = int(tokens[2])

        if CURRENT_PROCESS is not None:
            CURRENT_PROCESS.terminate()

        CURRENT_QUEUE = multiprocessing.Queue()
        t = threading.Thread(target=wait_for_current_queue)
        t.start()
        if depth == 0:
            process = multiprocessing.Process(
                target=itdep,
                args=(CURRENT_QUEUE, CURRENT_BOARD, CONFIG),
                kwargs={
                    "movetime": target_movetime(
                        CURRENT_BOARD,
                        movetime,
                        wtime,
                        btime,
                        winc,
                        binc,
                    ),
                    "last_search": LAST_SEARCH,
                },
                daemon=False,
            )
        else:
            process = multiprocessing.Process(
                target=itdep,
                args=(CURRENT_QUEUE, CURRENT_BOARD, CONFIG),
                kwargs={
                    "max_depth": depth,
                    "last_search": LAST_SEARCH,
                },
                daemon=False,
            )
        process.start()
        CURRENT_PROCESS = process
    return []


def wait_for_current_queue():
    global CURRENT_QUEUE
    global LAST_SEARCH
    while CURRENT_QUEUE is not None:
        try:
            last_search = CURRENT_QUEUE.get(timeout=1)
            if last_search is not None and last_search.end:
                LAST_SEARCH = last_search
            break
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) == 1:
        while True:
            line = input()
            for line in uci_parser(line):
                print(line)

    if sys.argv[1] == "--version":
        print(f"{CONFIG.version}")
        sys.exit()

    # if we don't know what to do, print the help
    print(("Usage:\n" f"  {sys.argv[0]}\n" f"  {sys.argv[0]} (-h | --help | --version)\n"))
    sys.exit()
