import time
import board
import search
import hashtable


def bestMove(fen, depth):
    b = board.Board(fen)
    for i in range(depth + 1):
        best_move = search.search(b, i)
        print(f"""\
info depth {best_move.depth} \
score cp {best_move.score} \
time {best_move.time / 1e9} \
nodes {best_move.nodes} \
{f"nps {int(best_move.nodes * 1e9 // max(0.0001, best_move.time))}" if best_move.time > 0 else " "}\
currmove {board.toUCI(best_move.move)} \
""")
    return board.toUCI(best_move)


if __name__ == "__main__":
    b = board.Board("6kr/p1nprppp/3p4/1p2p3/4P1qP/1P1B4/PBPP1PPR/RQ4K1 b - - 9 34")
    # board = b.Board("startpos")
    start_time = time.process_time()
    depth = 4
    for i in range(depth + 1):
        best_move = search.search(b, i)
        print(f"""\
info depth {best_move.depth} \
score cp {best_move.score} \
time {best_move.time / 1e9} \
nodes {best_move.nodes} \
{f"nps {int(best_move.nodes * 1e9 // max(0.0001, best_move.time))}" if best_move.time > 0 else " "}\
currmove {board.toUCI(best_move.move)} \
""")
    print(f"Hashtable:{len(hashtable.HASH_TABLE)},req:{hashtable.REQ},hits:{hashtable.HITS}")
