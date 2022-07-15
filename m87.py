#!/usr/bin/env python3
"""M87

Usage:
    m87
    m87 (-h | --help | --version)
"""

import sys
import time
import multiprocessing
from engine.constants import COLOR
from engine.board import Board
from engine.search import search
from engine.transposition_table import TranspositionTable
from engine.evaluation import eval_board
from engine.data_structures import toUCI

NAME = "M87"
VERSION = "{} 0.10.5".format(NAME)
AUTHOR = "nrobinaubertin"
CURRENT_BOARD = Board("startpos")
CURRENT_PROCESS = None
TRANSPOSITION_TABLE = None

def bestMove(board, max_time=0, max_depth=0, eval_guess=0, rand_count=1, transposition_table=None):
    current_eval = eval_guess
    if max_time != 0:
        start_time = time.process_time_ns()
        for i in range((10 if max_depth == 0 else max_depth)):
            best = search(board, depth=i, eval_guess=current_eval, rand_count=rand_count, transposition_table=transposition_table)
            current_eval = best.score
            used_time = max(1, (time.process_time_ns() - start_time) // 1000)
            print(
                ""
                + f"info depth {best.depth} "
                + f"score cp {best.score} "
                + f"time {int(best.time // 1e9)} "
                + f"nodes {best.nodes} "
                + (
                    "nps "
                    + str(int(best.nodes * 1e9 // max(0.001, best.time)))
                    + " "
                    if best.time > 0
                    else ""
                )
                + f"pv {' '.join([toUCI(x) for x in best.pv])}"
            )
            if (min(used_time, 1) + i) * 5 > (max_time - 1) // max(10, 40 - board.full_move) * 1000:
                break
    else:
        for i in range(max_depth + 1):
            best = search(board, depth=i, eval_guess=current_eval, transposition_table=transposition_table)
            current_eval = best.score
            print(
                ""
                + f"info depth {best.depth} "
                + f"score cp {best.score} "
                + f"time {int(best.time // 1e9)} "
                + f"nodes {best.nodes} "
                + (
                    "nps " + str(int(best.nodes * 1e9 // max(0.0001, best.time))) + " "
                    if best.time > 0
                    else ""
                )
                + f"pv {' '.join([toUCI(x) for x in best.pv])}"
            )

    print(f"bestmove {toUCI(best.move)}")
    return toUCI(best.move)

def stop_calculating():
    global CURRENT_PROCESS
    if CURRENT_PROCESS is not None:
        CURRENT_PROCESS.terminate()

def uci_parser(line):
    global CURRENT_BOARD
    tokens = line.strip().split()

    if not tokens:
        return []

    if tokens[0] == "eval":
        return [f"board: {eval_board(CURRENT_BOARD)}"]

    if tokens[0] == "print":
        return [str(CURRENT_BOARD)]

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
        output = TRANSPOSITION_TABLE.export()
        return [output]

    if len(tokens) == 1 and tokens[0] == "uci":
        return [
            "{} by {}".format(VERSION, AUTHOR),
            "id name {}".format(NAME),
            "id author {}".format(AUTHOR),
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
        CURRENT_BOARD = Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
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
            fen = "{0} {1} {2} {3} {4} {5}".format(
                tokens[1],
                tokens[2],
                tokens[3],
                tokens[4],
                tokens[5] if len(tokens) > 5 else 0,
                tokens[6] if len(tokens) > 6 else 0,
            )
            next_token = 7
        board = Board(fen)
        if len(tokens) > next_token and tokens[next_token] == "moves":
            for move in tokens[next_token + 1 :]:
                board.push(board.fromUCI(move))
        CURRENT_BOARD = board

    if len(tokens) > 1 and tokens[0] == "go":

        depth = None

        if len(tokens) > 8:
            if tokens[1] == "wtime":
                wtime = int(tokens[2])
            if tokens[3] == "btime":
                btime = int(tokens[4])
            if tokens[5] == "winc":
                winc = int(tokens[6])
            if tokens[7] == "binc":
                binc = int(tokens[8])

        if tokens[1] == "movetime":
            wtime = int(tokens[2])
            btime = int(tokens[2])
            winc = 0
            binc = 0

        if tokens[1] == "depth":
            depth = int(tokens[2])

        current_eval = eval_board(CURRENT_BOARD)

        global CURRENT_PROCESS
        if CURRENT_PROCESS is not None:
            CURRENT_PROCESS.terminate()

        if depth is None:
            my_time = wtime + winc
            if CURRENT_BOARD.turn == COLOR.BLACK:
                my_time = btime + binc
            process = multiprocessing.Process(
                    target=bestMove,
                    args=(CURRENT_BOARD,),
                    kwargs={
                        "max_time": my_time,
                        "max_depth": min(6, CURRENT_BOARD.full_move),
                        "eval_guess": current_eval,
                        "rand_count": max(1, 2 * (5 - CURRENT_BOARD.full_move)),
                        "transposition_table": TRANSPOSITION_TABLE
                    },
                    daemon=True,
                )
        else:
            process = multiprocessing.Process(
                    target=bestMove,
                    args=(CURRENT_BOARD,),
                    kwargs={
                        "max_depth": depth,
                        "eval_guess": current_eval,
                        "transposition_table": TRANSPOSITION_TABLE
                    },
                    daemon=True,
                )
        process.start()
        CURRENT_PROCESS = process
    return []

if __name__ == "__main__":
    with multiprocessing.Manager() as manager:
        TRANSPOSITION_TABLE = TranspositionTable(manager.dict())
        while True:
            line = input()
            for line in uci_parser(line):
                print(line)
