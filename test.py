import engine
import chess
import chess.variant
import random
from collections import namedtuple
import timeit

timelim = namedtuple("time_limit", "time white_clock white_inc black_clock black_inc")
t1 = timelim(10.0, None, None, None, None)
t2 = timelim(None, 60.0, 5.0, 60.0, 5.0)
# b = chess.Board()
# main.iterativeDeepening(b, t)
# main.iterativeDeepening(b, t2)

for str in [
    "standard",
    "antichess",
    "atomic",
    "kingofthehill",
    "racingkings",
    "horde",
    "3check",
    "crazyhouse",
]:
    btype = chess.variant.find_variant(str)
    b = btype()
    for i in range(1, 30):
        ms = list(b.legal_moves)
        if len(ms):
            m = random.choice(ms)
            b.push(m)
        else:
            break
    if b.is_game_over():
        print(f"aborted test of {str}, game over after test moves\n")
        continue
    if str == "crazyhouse":
        print(b.pockets)
    print(f"now testing {str}\n")

    engine.iterativeDeepening(b, t1)
    engine.iterativeDeepening(b, t2)
    print()

b = chess.Board()
for i in range(1, 30):
    ms = list(b.legal_moves)
    if len(ms):
        m = random.choice(ms)
        b.push(m)
    else:
        break

print(
    timeit.timeit(
        stmt="main.evaluateStandard(b, 1, True)",
        setup="import main; import chess; b = chess.Board('2b1kb1r/1r3ppp/nppp4/1P3p2/p2P2n1/N1P1P2B/P4P1P/R1BK2NR w k - 0 16'); ",
        number=10000,
    )
)
print(
    timeit.timeit(
        "main.evaluateStandard(b, 1, False)",
        setup="import main; import chess; b = chess.Board('2b1kb1r/1r3ppp/nppp4/1P3p2/p2P2n1/N1P1P2B/P4P1P/R1BK2NR w k - 0 16'); ",
        number=10000,
    )
)

print("Test succeeded!")
