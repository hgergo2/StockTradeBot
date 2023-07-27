import statisticsInfo
from strategies import support_and_resistance_strategy, ema_strategy

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

#['NVDA', 'NFLX', 'AMC', 'CVNA', 'AMD']
#symbols = ['NVDA']
#statistics_summary = statisticsInfo.StatsSummary()
#for symbol in symbols:
#    #result = ema_strategy.strategy(symbol).run_strategy(show_chart=True)
#    #result = adx_strategy.strategy(symbol).run_strategy(show_chart=True)
#    result = support_and_resistance_strategy.strategy(symbol).run_strategy(show_chart=True)
#
#    #result.show_statistics()

#statistics_summary.show_stats()

app = Flask(__name__)


@app.route('/test/')
def test():
    return 'test'

@app.route('/strategy/<symbol>/<strat_name>/')
@cross_origin()
def get_strat_chart(symbol, strat_name):
    return support_and_resistance_strategy.strategy(symbol).run_strategy(show_chart=False)[1].to_json()


if __name__ == "__main__":
    app.run(debug=True)
