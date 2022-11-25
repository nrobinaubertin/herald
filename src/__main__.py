#!/usr/bin/env python3

import sys
import multiprocessing
import engine.board as board
from engine.transposition_table import TranspositionTable
from engine.evaluation import eval_pst
from engine.data_structures import to_uci, Board
from engine.iterative_deepening import itdep
from engine.algorithms import minimax, alphabeta, negac
from engine.time_management import target_movetime

NAME = "Herald"
VERSION = f"{NAME} 0.15.2"
AUTHOR = "nrobinaubertin"
CURRENT_BOARD = board.from_fen("startpos")
CURRENT_PROCESS = None
MULTIPROCESSING_MANAGER = multiprocessing.Manager()
TRANSPOSITION_TABLE = None

ALGS = {
    "minimax": minimax,
    "alphabeta": alphabeta,
    "negac": negac,
}
CURRENT_ALG = "alphabeta"


def stop_calculating() -> None:
    global CURRENT_PROCESS
    if CURRENT_PROCESS is not None:
        CURRENT_PROCESS.terminate()


def uci_parser(line: str) -> list[str]:
    global CURRENT_ALG
    global CURRENT_BOARD
    global TRANSPOSITION_TABLE
    tokens = line.strip().split()

    if not tokens:
        return []

    if tokens[0] == "alg":
        CURRENT_ALG = tokens[1] if tokens[1] in ALGS else "alphabeta"
        return [f"using {CURRENT_ALG}"]

    if tokens[0] == "eval":
        return [f"board: {eval_pst(CURRENT_BOARD)}"]

    if tokens[0] == "print":
        return [board.to_string(CURRENT_BOARD)]

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
                return len(list(board.moves(b)))

            nodes = 0
            for move in board.moves(b):
                curr_board = board.push(b, move)
                nodes += execute(curr_board, depth - 1)

            return nodes
        for move in board.moves(CURRENT_BOARD):
            b = board.push(CURRENT_BOARD, move)
            nodes = execute(b, int(tokens[1]) - 1)
            to_display.append(f"{to_uci(move)}: {nodes}")
            total += nodes
        to_display.append(f"Nodes: {total}")
        return to_display

    if (
        __debug__
        and len(tokens) > 1
        and tokens[0] == "tt"
        and tokens[1] == "stats"
    ):
        if TRANSPOSITION_TABLE is not None:
            stats = TRANSPOSITION_TABLE.stats()
            stats_str = (
                f"SHALLOW_HITS: {stats['SHALLOW_HITS']}, "
                f"HITS: {stats['HITS']}, "
                f"REQ: {stats['REQ']}, "
                f"LEN: {stats['LEN']}, "
                f"ADD: {stats['ADD']}, "
                f"ADD_BETTER: {stats['ADD_BETTER']}"
            )
            return [stats_str]
        else:
            return [""]

    if len(tokens) > 1 and tokens[0] == "tt" and tokens[1] == "remove":
        TRANSPOSITION_TABLE = None
        return [
            "tt removed",
        ]

    if len(tokens) > 1 and tokens[0] == "tt" and tokens[1] == "init":
        TRANSPOSITION_TABLE = TranspositionTable(MULTIPROCESSING_MANAGER.dict())
        return [
            "tt initialized",
        ]

    if len(tokens) == 1 and tokens[0] == "uci":
        return [
            f"{VERSION} by {AUTHOR}",
            f"id name {NAME}",
            f"id author {AUTHOR}",
            # fake some options
            "option name Hash type spin default 16 min 1 max 33554432",
            "option name Move Overhead type spin default 10 min 0 max 5000",
            "option name Threads type spin default 1 min 1 max 1",
            "uciok",
        ]

    if tokens[0] == "stop":
        stop_calculating()

    if tokens[0] == "quit":
        stop_calculating()
        sys.exit()

    if tokens[0] == "play":
        move = board.from_uci(CURRENT_BOARD, tokens[1])
        CURRENT_BOARD = board.push(CURRENT_BOARD, move)

    if tokens[0] == "ucinewgame":
        CURRENT_BOARD = board.from_fen(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )
        return []

    if tokens[0] == "isready":
        return [
            "readyok",
        ]

    if len(tokens) > 1 and tokens[0] == "position":
        if tokens[1] == "startpos":
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
            next_token = 2
        else:
            fen = (
                f"{tokens[1]} "
                f"{tokens[2]} {tokens[3]} {tokens[4]} "
                f"{tokens[5] if len(tokens) > 5 else 0} "
                f"{tokens[6] if len(tokens) > 6 else 0}"
            )
            next_token = 7
        b = board.from_fen(fen)
        if len(tokens) > next_token and tokens[next_token] == "moves":
            for move_str in tokens[next_token + 1:]:
                b = board.push(b, board.from_uci(b, move_str))
        CURRENT_BOARD = b

    if len(tokens) > 1 and tokens[0] == "go":

        depth = None
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

        current_eval = eval_pst(CURRENT_BOARD)

        global CURRENT_PROCESS
        if CURRENT_PROCESS is not None:
            CURRENT_PROCESS.terminate()

        if depth is None:
            process = multiprocessing.Process(
                target=itdep,
                args=(CURRENT_BOARD,),
                kwargs={
                    "movetime": target_movetime(
                        CURRENT_BOARD.turn,
                        movetime,
                        wtime,
                        btime,
                        winc,
                        binc,
                    ),
                    "alg_fn": ALGS[CURRENT_ALG],
                    "eval_guess": current_eval,
                    "rand_count": max(1, 2 * (4 - CURRENT_BOARD.full_move)),
                    "transposition_table": TRANSPOSITION_TABLE,
                },
                daemon=False,
            )
        else:
            process = multiprocessing.Process(
                target=itdep,
                args=(CURRENT_BOARD,),
                kwargs={
                    "max_depth": depth,
                    "alg_fn": ALGS[CURRENT_ALG],
                    "eval_guess": current_eval,
                    "transposition_table": TRANSPOSITION_TABLE,
                },
                daemon=False,
            )
        process.start()
        CURRENT_PROCESS = process
    return []


if __name__ == "__main__":

    if len(sys.argv) == 1:
        while True:
            line = input()
            for line in uci_parser(line):
                print(line)

    if sys.argv[1] == "--version":
        print(f"{VERSION}")
        sys.exit()

    # if we don't know what to do, print the help
    print(
        (
            "Usage:\n"
            f"  {sys.argv[0]}\n"
            f"  {sys.argv[0]} (-h | --help | --version)\n"
        )
    )
    sys.exit()
