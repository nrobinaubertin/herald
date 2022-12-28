#!/usr/bin/env python3

import os
import sys
import multiprocessing
import json
import engine.board as board
from engine.data_structures import to_uci, Board
from engine.iterative_deepening import itdep
from engine.analysis import fen_analysis
from engine.time_management import target_movetime
from engine.configuration import Config
from engine.evaluation import eval_simple, eval_pst, eval_new
from engine.move_ordering import no_ordering, mvv_lva
from engine.algorithms import alphabeta

CURRENT_BOARD = board.from_fen("startpos")
CURRENT_PROCESS = None

CONFIG = Config({
    "version": "0.19.3",
    "alg_fn": alphabeta,
    "move_ordering_fn": mvv_lva,
    "eval_fn": eval_new,
    "quiescence_search": True,
    "quiescence_depth": 5,
    "use_transposition_table": True,
    "use_qs_transposition_table": True,
})

# load config at default location
if os.access("config.json", os.R_OK):
    with open("config.json", "r") as output_file:
        CONFIG._config = json.load(output_file)

# load opening book at default location
if os.access("opening_book", os.R_OK):
    with open("opening_book", "r") as output_file:
        CONFIG.opening_book = json.load(output_file)


def stop_calculating() -> None:
    global CURRENT_PROCESS
    if CURRENT_PROCESS is not None:
        CURRENT_PROCESS.terminate()


def uci_parser(line: str) -> list[str]:
    global CURRENT_ALG
    global CURRENT_BOARD
    global CURRENT_PROCESS
    tokens = line.strip().split()

    if not tokens:
        return []

    if tokens[0] == "eval":
        return [f"board: {CONFIG.eval_fn(CURRENT_BOARD)}"]

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

    if len(tokens) == 2 and tokens[0] == "load_book":
        with open(tokens[1], "r") as output_file:
            CONFIG.opening_book = json.load(output_file)

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

    if len(tokens) > 1 and tokens[0] == "analysis":

        input = tokens[1]
        output = tokens[2]
        depth = int(tokens[3])
        branch_factor = int(tokens[4])

        if CURRENT_PROCESS is not None:
            CURRENT_PROCESS.terminate()

        process = multiprocessing.Process(
            target=fen_analysis,
            args=(input, output),
            kwargs={
                "depth": depth,
                "branch_factor": branch_factor,
            },
            daemon=False,
        )
        process.start()
        CURRENT_PROCESS = process

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

        if depth == 0:
            process = multiprocessing.Process(
                target=itdep,
                args=(CURRENT_BOARD, CONFIG),
                kwargs={
                    "movetime": target_movetime(
                        CURRENT_BOARD.turn,
                        movetime,
                        wtime,
                        btime,
                        winc,
                        binc,
                    ),
                },
                daemon=False,
            )
        else:
            process = multiprocessing.Process(
                target=itdep,
                args=(CURRENT_BOARD, CONFIG),
                kwargs={
                    "max_depth": depth,
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
        print(f"{CONFIG.version}")
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
