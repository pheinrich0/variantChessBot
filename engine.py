import chess
from chess import Board
import chess.variant
from chess.engine import PlayResult, InfoDict, PovScore, Cp
import sys
import time


try:
    from variantChessBot.pst import table
except:
    from pst import table
#

mateScore = 10000


def negamax(
    board: Board,
    depth: int,
    ply: int,
    breakTime,
    alpha: int = -sys.maxsize,
    beta: int = sys.maxsize,
) -> tuple[int, chess.Move]:
    if depth == 0 or board.is_game_over(claim_draw=board.ply() > 40):
        return evaluate(board, depth), 0
    if board.is_check():
        depth += 1
    bestScore = -sys.maxsize
    bestMove = chess.Move(chess.A2, chess.A4)
    sortKey = lambda m: materialDiff(m, board)
    ms = list(board.legal_moves)
    # no influence of sorting at the horizon
    if depth > 1:
        ms.sort(key=sortKey)
    for m in ms:
        board.push(m)
        tempScore = -negamax(board, depth - 1, ply + 1, breakTime, -beta, -alpha)[0]
        board.pop()
        if tempScore > bestScore:
            bestScore = tempScore
            bestMove = m
        if bestScore > alpha:
            alpha = bestScore
        if alpha >= beta:
            break
        if time.time() >= breakTime:
            break
    return bestScore, bestMove


matScores = [100, 315, 330, 500, 900, 200]


def evaluate(board: Board, depth: int) -> int:
    result = board.outcome(claim_draw=board.ply() > 70)
    if result:
        us = board.turn
        return (result.winner is us) * mateScore - depth - (result.winner is (not us)) * mateScore + depth
    bType = type(board)
    if bType == chess.variant.AntichessBoard:
        return evaluateAnti(board, depth)
    elif bType == chess.variant.AtomicBoard:
        return evaluateAtomic(board, depth)
    elif bType == chess.variant.KingOfTheHillBoard:
        return evaluateKOTH(board, depth)
    elif bType == chess.variant.RacingKingsBoard:
        return evaluateRacing(board, depth)
    elif bType == chess.variant.HordeBoard:
        return evaluateHorde(board, depth)
    elif bType == chess.variant.ThreeCheckBoard:
        return evaluate3check(board, depth)
    elif bType == chess.variant.CrazyhouseBoard:
        return evaluateCrazyhouse(board, depth)
    else:
        return evaluateStandard(board, depth)


def evaluateStandard(board: Board, depth: int, usePST: bool = True) -> int:
    eval = 0
    us = board.turn
    opp = not us
    for pt in range(1, 7):
        usPT = board.pieces(pt, us)
        eval += len(usPT) * matScores[pt - 1]
        oppPT = board.pieces(pt, opp)
        eval -= len(oppPT) * matScores[pt - 1]
        if usePST:
            for sq in usPT:
                sq = chess.square_mirror(sq) if us else sq
                eval += table[(pt - 1) * 64 + sq]
            for sq in oppPT:
                sq = chess.square_mirror(sq) if opp else sq
                eval -= table[(pt - 1) * 64 + sq]
    return eval


def evaluateAnti(board: Board, depth: int) -> int:
    eval = -evaluateStandard(board, depth)
    return eval


def evaluateAtomic(board: Board, depth: int) -> int:
    eval = evaluateStandard(board, depth)
    return eval


def evaluateKOTH(board: Board, depth: int) -> int:
    eval = evaluateStandard(board, depth)
    return eval


def evaluateRacing(board: Board, depth: int) -> int:
    eval = evaluateStandard(board, depth, False)
    eval += chess.square_rank(board.king(board.turn)) * 100
    eval -= chess.square_rank(board.king(not board.turn)) * 100
    return eval


def evaluateHorde(board: Board, depth: int) -> int:
    eval = evaluateStandard(board, depth)
    return eval


def evaluate3check(board: Board, depth: int) -> int:
    eval = evaluateStandard(board, depth)
    eval += (3 - board.remaining_checks[board.turn]) ^ 2 * 250
    eval -= (3 - board.remaining_checks[not board.turn]) ^ 2 * 300
    return eval


def evaluateCrazyhouse(board: Board, depth: int) -> int:
    eval = 0
    us = board.turn
    opp = not us
    pockets = board.pockets
    for pt in range(1, 6):
        eval += (pockets[us].count(pt) * matScores[pt - 1]) // 3
        eval -= (pockets[opp].count(pt) * matScores[pt - 1]) // 3
    return eval


def materialDiff(move: chess.Move, board: Board):
    taken = board.piece_at(move.to_square)
    if taken:
        return taken.piece_type - board.piece_at(move.from_square).piece_type
    else:
        return -10


def iterativeDeepening(board: Board, time_limit, uciLogging: bool = False):
    us = board.turn
    avtime = 0
    print(time_limit)
    our_clock = 0
    if hasattr(time_limit, "time") and time_limit.time is not None:
        avtime = time_limit.time / 2
        our_clock = 20
    else:
        if us:
            our_clock = time_limit.white_clock
            avtime += time_limit.white_clock / 50
            inc = time_limit.white_inc
            if inc * 3 < avtime:
                avtime += (inc * 3) / 4
        else:
            our_clock = time_limit.black_clock
            avtime += time_limit.black_clock / 50
            inc = time_limit.black_inc
            if inc * 3 < avtime:
                avtime += (inc * 3) / 4
    breakTime = min(2 * avtime, 0.7 * our_clock)
    avtime /= 2
    avtime = min(breakTime / 3, avtime)
    breakTime += time.time()
    bestMove = list(board.legal_moves)[0]
    oldbestMove = bestMove
    score = 0
    starttime = time.time()
    depth = 1
    while (time.time() - starttime < avtime) and depth < 100:
        depth += 1
        score, oldbestMove = negamax(board, depth, 1, breakTime)
        if time.time() < breakTime:
            bestMove = oldbestMove
        else:
            break
        if uciLogging:
            print(
                f"info depth {depth} score cp {score} time {round((time.time()-starttime)*1000)} pv {bestMove.uci()}"
            )
    if uciLogging:
        print(f"bestmove {bestMove.uci()}")
    info = InfoDict(
        score=PovScore(Cp(score), us),
        pv=[bestMove],
        depth=depth,
        time=time.time() - starttime,
    )
    return PlayResult(bestMove, None, info=info)
