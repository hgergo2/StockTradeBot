import statisticsInfo
import strategy

#['NVDA', 'NFLX', 'AMC', 'COIN', 'CVNA', 'AMD']
symbols = ['NVDA', 'TSLA', 'CVNA']
statistics_summary = statisticsInfo.StatsSummary()
for symbol in symbols:
    result = strategy.strategy(symbol).run_strategy(show_chart=False)
    result.show_statistics()
    statistics_summary.add(result)


statistics_summary.show_stats()


