#!/usr/bin/env python3

import os
import sys
import multiprocessing
from engine.constants import COLOR
import engine.board as board
from engine.search import search
from engine.transposition_table import TranspositionTable
from engine.evaluation import eval_pst
from engine.data_structures import to_uci
from engine.best_move import best_move

NAME = "Herald"
VERSION = f"{NAME} 0.12.2"
AUTHOR = "nrobinaubertin"
CURRENT_BOARD = board.from_fen("startpos")
CURRENT_PROCESS = None
TRANSPOSITION_TABLE = None


def stop_calculating():
    global CURRENT_PROCESS
    if CURRENT_PROCESS is not None:
        CURRENT_PROCESS.terminate()


def uci_parser(line):
    global CURRENT_BOARD
    global TRANSPOSITION_TABLE
    tokens = line.strip().split()

    if not tokens:
        return []

    if tokens[0] == "eval":
        return [f"board: {eval_pst(CURRENT_BOARD)}"]

    if tokens[0] == "print":
        return [board.to_string(CURRENT_BOARD)]

    if tokens[0] == "moves":
        return [", ".join([to_uci(m) for m in board.moves(CURRENT_BOARD)])]

    if len(tokens) > 1 and tokens[0] == "tt" and tokens[1] == "stats":
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

    if len(tokens) > 1 and tokens[0] == "tt" and tokens[1] == "export":
        if len(tokens) > 2 and tokens[2] != "":
            filename = tokens[2]
        output = TRANSPOSITION_TABLE.export(filename)
        return [output]

    if len(tokens) > 2 and tokens[0] == "tt" and tokens[1] == "import":
        filename = tokens[2]
        TRANSPOSITION_TABLE.import_table(filename)
        return []

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

    if tokens[0] == "ucinewgame":
        CURRENT_BOARD = board.from_fen(
            "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        )
        return []

    if tokens[0] == "isready":
        return [
            "readyok",
        ]

    if tokens[0] == "nott":
        TRANSPOSITION_TABLE = None
        return [
            "tt removed",
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
            for move in tokens[next_token + 1:]:
                b = board.push(b, board.from_uci(b, move))
        CURRENT_BOARD = b

    if len(tokens) > 1 and tokens[0] == "go":

        depth = None
        wtime = 0
        btime = 0
        winc = 0
        binc = 0

        if tokens[1] == "movetime":
            wtime = int(tokens[2])
            btime = int(tokens[2])
            winc = 0
            binc = 0

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
            max_time = wtime
            inc_time = winc
            if CURRENT_BOARD.turn == COLOR.BLACK:
                max_time = btime
                inc_time = binc

            max_time = min(40000, max_time)

            process = multiprocessing.Process(
                target=best_move,
                args=(CURRENT_BOARD,),
                kwargs={
                    "max_time": max_time // 1000,
                    "inc_time": inc_time // 1000,
                    "eval_guess": current_eval,
                    "rand_count": max(1, 2 * (4 - CURRENT_BOARD.full_move)),
                    "transposition_table": TRANSPOSITION_TABLE,
                },
                daemon=False,
            )
        else:
            process = multiprocessing.Process(
                target=best_move,
                args=(CURRENT_BOARD,),
                kwargs={
                    "max_depth": depth,
                    "eval_guess": current_eval,
                    "transposition_table": TRANSPOSITION_TABLE,
                },
                daemon=False,
            )
        process.start()
        CURRENT_PROCESS = process
    return []


if __name__ == "__main__":

    if len(sys.argv) == 1 or sys.argv[1] == "--import-memory":
        with multiprocessing.Manager() as manager:
            TRANSPOSITION_TABLE = TranspositionTable(manager.dict())

            # check if standard path for memory exists
            memory = os.path.join(os.path.abspath(os.path.dirname(__file__)), "memory")
            filename = sys.argv[2] if len(sys.argv) > 2 else ""
            if os.path.exists(memory) and filename == "":
                filename = "memory"

            if filename != "":
                TRANSPOSITION_TABLE.import_table(filename)

            while True:
                line = input()
                for line in uci_parser(line):
                    print(line)

    if sys.argv[1] == "--version":
        print(f"{VERSION}")
        sys.exit()

    if sys.argv[1] == "--prepare-memory":
        depth = int(sys.argv[2])
        b = board.from_fen("startpos")
        transposition_table = TranspositionTable({})

        if len(sys.argv) > 4 and sys.argv[3] == "--from":
            transposition_table.import_table(sys.argv[4])

        for j in range(depth + 1):
            for i in range(5):
                best = search(
                    b,
                    depth=i,
                    transposition_table=transposition_table,
                )
                print(
                    ""
                    + f"info depth {best.depth} "
                    + f"score cp {best.score} "
                    + f"time {int(best.time // 1e9)} "
                    + f"nodes {best.nodes} "
                    + (
                        "nps "
                        + str(int(best.nodes * 1e9 // max(0.0001, best.time)))
                        + " "
                        if best.time > 0
                        else ""
                    )
                    + f"pv {' '.join([to_uci(x) for x in best.pv])}"
                )
            print(f"--> {to_uci(best.move)}")
            board.push(b, best.move)

        output = transposition_table.export_table("memory")
        print(output)
        sys.exit()

    # if we don't know what to do, print the help
    print(
        (
            "Usage:\n"
            "   run.py [--import-memory <filename>]\n"
            "   run.py --prepare-memory <depth> [--from <filename>]\n"
            "   run.py (-h | --help | --version)\n"
        )
    )
    sys.exit()
