import chess
import chess.variant
from chess.engine import PlayResult, InfoDict, PovScore, Cp
import sys
import time

mateScore = 10000


def negamax(board, depth, ply, breakTime, alpha=-sys.maxsize, beta=sys.maxsize):
    if depth == 0 or board.is_game_over(claim_draw=board.ply() > 70):
        return evaluate(board, depth), 0

    bestScore = -sys.maxsize
    bestMove = chess.Move(chess.A2, chess.A4)
    for m in board.legal_moves:
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


def evaluate(board, depth):
    result = board.outcome(claim_draw=board.ply() > 70)
    if result:
        us = board.turn
        return (result.winner is us) * mateScore * (depth + 1) - (
            result.winner is not us
        ) * mateScore * (depth + 1)
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
        return evaluateStandard(board, depth)
    else:
        return evaluateStandard(board, depth)


def evaluateStandard(board, depth):
    eval = 0
    us = board.turn
    opp = not us
    for pt in range(1, 7):
        eval += len(board.pieces(pt, us)) * matScores[pt - 1]
        eval -= len(board.pieces(pt, opp)) * matScores[pt - 1]
    return eval


def evaluateAnti(board, depth):
    eval = -evaluateStandard(board, depth)
    return eval


def evaluateAtomic(board, depth):
    eval = evaluateStandard(board, depth)
    return eval


def evaluateKOTH(board, depth):
    eval = evaluateStandard(board, depth)
    return eval


def evaluateRacing(board, depth):
    eval = evaluateStandard(board, depth)
    eval += chess.square_rank(board.king(board.turn))*100
    eval -= chess.square_rank(board.king(not board.turn))*100
    return eval


def evaluateHorde(board, depth):
    eval = evaluateStandard(board, depth)
    return eval


def evaluate3check(board, depth):
    eval = evaluateStandard(board, depth)
    eval += (3 - board.remaining_checks[board.turn])^ 2 * 250
    eval -= (3 - board.remaining_checks[not board.turn])^ 2 * 250
    return eval


def evaluateCrazyhouse(board, depth):
    eval = 0
    us = board.turn
    opp = not us
    pockets = board.pockets
    for pt in range(1, 6):
        eval += (pockets[us].count(pt) * matScores[pt - 1]) // 3
        eval -= (pockets[opp] * matScores[pt - 1]) // 3


def iterativeDeepening(board, time_limit, uciLogging=False):
    us = board.turn
    avtime = 0
    print(time_limit)
    our_clock = 0
    if hasattr(time_limit, "time") and time_limit.time is not None:
        avtime = time_limit.time / 5
    else:
        if us:
            our_clock = time_limit.white_clock
            avtime += time_limit.white_clock / 70
            inc = time_limit.white_inc
            if inc * 3 < avtime:
                avtime += (inc * 9) / 15
        else:
            our_clock = time_limit.black_clock
            avtime += time_limit.black_clock / 70
            inc = time_limit.black_inc
            if inc * 3 < avtime:
                avtime += (inc * 9) / 15
    breakTime = time.time() + min(avtime, 0.7 * our_clock)
    avtime /= 2
    avtime = min(breakTime / 2, avtime)
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
