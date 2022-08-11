import sys
import pexpect


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
    h = []
    h.append(Bot(sys.argv[1]))
    h.append(Bot(sys.argv[2]))
    moves = []
    should_break = 0
    evaluation = 0
    for i in range(100):
        h[i % 2].pos_moves(moves)
        move = h[i % 2].gotime(10)
        move = move.split()[-1]
        moves.append(move)
        if len(sys.argv) > 3 and sys.argv[3] == "print":
            h[i % 2].print()
        evaluation = int(h[i % 2].eval().split()[-1])
        if len(sys.argv) > 3 and sys.argv[3] == "print":
            print(evaluation)
        if abs(evaluation) > 1000:
            should_break += 1
        if should_break > 4:
            break
    h[0].quit()
    h[1].quit()
    if abs(evaluation) > 500:
        if evaluation > 0:
            print(sys.argv[1])
        else:
            print(sys.argv[2])
