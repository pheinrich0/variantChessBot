import os
import main
import chess
import chess.variant

from collections import namedtuple

timelim = namedtuple("time_limit", "time")

from flask import Flask
from flask import request

app = Flask(__name__)


@app.post("/")
def hello_world():
    data = request.get_data(as_text=True)
    variant, fen, time = data.splitlines()
    btype = chess.variant.find_variant(variant)
    if fen == "startpos":
      fen = btype.starting_fen
    board = btype(fen)
    time = int(time)
    lim = timelim(time/1000)
    result = main.iterativeDeepening(board, lim)
    return f"{result.info['score'].relative}\n{result.move}"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))