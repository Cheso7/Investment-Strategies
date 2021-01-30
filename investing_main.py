'''
@author: Cheso7
TODO: Fix magnitude of info_filter 
'''
import investing_strategy
import data_collection

#Use this to run with chosen tickers
tickers = ["AMD","NVDA","AAPL",'GME', 'AME', 'BB']

#Use this to import a list of tickers from an index on Wikipedia
# tickers_list = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
# tickers = data_collection.get_tickers(tickers_list)

#Parameters
years = 5 # years of data to collect
interval = '1mo'

def main():
    # ohlc = data_collection.ohlc(tickers, years, interval)

    # financials_cy, financials_py, financials_py2 = data_collection.get_financials(tickers)
    statistics_dir_cy = data_collection.get_statistics(tickers)

    # df_cy = data_collection.info_filter(financials_cy)
    # df_py = data_collection.info_filter(financials_py)
    # dy_py2 = data_collection.info_filter(financials_py2)
    stats_cy = data_collection.info_filter_stats(statistics_dir_cy)

    # piotroski = investing_strategy.piotroski(df_cy, df_py, dy_py2,tickers)
    # magic = investing_strategy.magic_formula(df_cy, stats_cy, tickers)
    shorted = investing_strategy.most_shorted(stats_cy, tickers)
    return

main()

