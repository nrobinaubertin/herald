"""
versus.py

Usage:
    versus.py <bot1> <bot2> [--print] [--matches=<matches>]
    versus.py -h | --help

Options:
  --print               Print board and evaluation on each move
  --matches=<matches>   Do <matches> between the bots instead of 1
  -h --help             Show this screen.
"""

import sys

import pexpect
from docopt import docopt


class Bot():
    def __init__(self, path):
        self.process = pexpect.spawn(path)

    def print(self):
        self.process.sendline('print')
        self.process.expect_exact('\r\n')
        for _ in range(13):
            self.process.expect_exact('\r\n')
            print(self.process.before.decode())

    def godepth(self, depth: int) -> str:
        self.process.sendline(f"go depth {depth}")
        self.process.expect('bestmove \\w+')
        ret = self.process.after.decode()
        self.process.expect_exact('\r\n')
        return ret

    def gotime(self, time: int) -> str:
        self.process.sendline(f"go movetime {time * 1000}")
        self.process.expect('bestmove \\w+')
        ret = self.process.after.decode()
        self.process.expect_exact('\r\n')
        return ret

    def command(self, cmd):
        self.process.sendline(cmd)
        self.process.expect_exact('\r\n')

    def position(self, pos):
        self.process.sendline(f"position {pos}")
        self.process.expect_exact('\r\n')

    def eval(self):
        self.process.sendline("eval")
        self.process.expect('board: -?\\w+')
        ret = self.process.after.decode()
        self.process.expect_exact('\r\n')
        return ret

    def quit(self):
        self.process.sendline('quit')
        self.process.expect(pexpect.EOF)

    def pos_moves(self, moves):
        if len(moves) > 0:
            self.position(f'startpos moves {" ".join(moves)}')
        else:
            self.position('startpos')


if __name__ == "__main__":
    args = docopt(str(__doc__))

    h = []
    h.append({
        "bot": Bot(sys.argv[1]),
        "score": 0
    })
    h.append({
        "bot": Bot(sys.argv[2]),
        "score": 0
    })

    matches = int(args['--matches']) if args['--matches'] else 1

    for i in range(matches):
        print(f"[{i + 1}/{matches}]")
        h[0]["bot"].position("startpos")
        h[1]["bot"].position("startpos")
        moves = []
        should_break = 0
        evaluation = 0
        for i in range(50):
            try:
                h[i % 2]["bot"].pos_moves(moves)
                move = h[i % 2]["bot"].gotime(10)
            except Exception as exc:
                print(moves)
                sys.exit(exc)
            move = move.split()[-1]
            if move == "nomove":
                if evaluation > 0:
                    h[0]["score"] += 1
                else:
                    h[1]["score"] += 1
                break
            moves.append(move)
            if args['--print']:
                h[i % 2]["bot"].print()
            evaluation = int(h[i % 2]["bot"].eval().split()[-1])
            if args['--print']:
                print(evaluation)
            if abs(evaluation) > 1000:
                should_break += 1
            if should_break > 4:
                break
        if abs(evaluation) > 500:
            if evaluation > 0:
                h[0]["score"] += 1
            else:
                h[1]["score"] += 1
    h[0]["bot"].quit()
    h[1]["bot"].quit()
    print([b["score"] for b in h])
