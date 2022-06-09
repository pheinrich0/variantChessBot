import chess
import chess.variant
from chess.engine import PlayResult, InfoDict, PovScore, Cp

import time

mateScore = 10000


def negamax(board, depth, ply, alpha=-10000000, beta=10000000):
    if board.is_game_over():
        result = board.outcome()
        us = board.turn
        return (result.winner is us) * mateScore - (result.winner is not us) * mateScore, 0
    elif depth == 0:
        return -evaluate(board, depth), 0

    bestScore = -100000
    bestMove = chess.Move(chess.A2, chess.A4)
    for m in board.legal_moves:
        board.push(m)
        tempScore = -negamax(board, depth - 1, ply + 1, -beta, -alpha)[0]
        board.pop()
        if tempScore > bestScore:
            bestScore = tempScore
            bestMove = m
            if bestScore > alpha:
                alpha = bestScore
        if alpha >= beta:
            break
    return bestScore, bestMove


matScores = [100, 315, 330, 500, 900, 200]


def evaluate(board, depth):
    result = board.outcome()
    if result:
        us = board.turn
        return (result.winner is us) * mateScore * (depth + 1) - (
            result.winner is not us
        ) * mateScore * (depth + 1)

    bType = type(board).uci_variant
    if bType == chess.variant.AntichessBoard:
        return evaluateAnti(board, depth)
    else:
        return evaluateStandard(board, depth)


def evaluateStandard(board, depth):
    eval = 0
    for pt in range(1, 7):
        eval += len(board.pieces(pt, 1)) * matScores[pt - 1]
        eval -= len(board.pieces(pt, 0)) * matScores[pt - 1]
    if board.turn:
        return eval
    else:
        return -eval


def evaluateAnti(board, depth):
    return -evaluateStandard(board, depth)


def iterativeDeepening(board, time_limit):
    us = board.turn
    avtime = 0
    print(time_limit)
    if hasattr(time_limit, "time") and time_limit.time is not None:
        avtime = time_limit.time / 5
    else:
        if us:
            avtime += time_limit.white_clock / 100
            inc = time_limit.white_inc
            if inc * 3 < avtime:
                avtime += (inc * 7) / 15
        else:
            avtime += time_limit.black_clock / 100
            inc = time_limit.black_inc
            if inc * 3 < avtime:
                avtime += (inc * 7) / 15
    avtime /= 2
    bestMove = list(board.legal_moves)[0]
    score = 0
    starttime = time.time()
    depth = 1
    while (time.time() - starttime < avtime) and depth < 100:
        depth += 1
        score, bestMove = negamax(board, depth, 1)
        print(
            f"info depth {depth} score cp {score} time {round((time.time()-starttime)*1000)} pv {bestMove.uci()}\n"
        )
    print(f"bestmove {bestMove.uci()}\n")
    info = InfoDict(
        score=PovScore(Cp(score), us),
        pv=[bestMove],
        depth=depth,
        time=time.time() - starttime,
    )
    return PlayResult(bestMove, None, info=info)
