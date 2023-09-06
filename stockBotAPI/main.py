from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

import mongo_handler

app = Flask(__name__)

@app.route('/test/')
def test():
    return 'Bing Bong'


@app.route('/strategy/<symbol>/<strat_name>/')
@cross_origin()
def get_strat_chart(symbol, strat_name):
    return mongo_handler.get_chart(symbol, strat_name)


@app.route('/positions/')
@cross_origin()
def get_position():
    symbol = request.args.get('symbol')
    strat_name = request.args.get('strat_name')
    active = request.args.get('active')

    return mongo_handler.get_positions(symbol, strat_name, active)

@app.route('/statistics/')
@cross_origin()
def get_statistics():

    return mongo_handler.get_statistics()


if __name__ == "__main__":
    app.run(debug=True)


