import os
import engine
import chess
import chess.variant
import functions_framework

from collections import namedtuple

timelim = namedtuple("time_limit", "time")

#from flask import Flask
#from flask import request

#app = Flask(__name__)


#@app.post("/")
@functions_framework.http
def hello_world(request):
    data = request.get_data(as_text=True)
    variant, fen, time = data.splitlines()
    btype = chess.variant.find_variant(variant)
    if fen == "startpos":
      fen = btype.starting_fen
    board = btype(fen)
    time = int(time)
    lim = timelim(time/1000)
    result = engine.iterativeDeepening(board, lim, True)
    return f"{result.info['score'].relative}\n{result.move}"


#if __name__ == "__main__":
#    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))