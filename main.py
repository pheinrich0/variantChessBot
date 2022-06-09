import chess
import sys
sys.path.append("../lichess-bot/")
import strategies

class VariantBot(MinimalEngine):
   def search(self, board, time_limit, ponder, draw_offered):
      return PlayResult(random.choice(list(board.legal_moves)), None)