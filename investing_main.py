import investing_data
import investing_strategy

#Use this to run with chosen tickers
tickers = ["MMM","AXP","AAPL"]

#Use this to import a list of tickers from an index on Wikipedia
# tickers = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

#Parameters
years = 5 # years of data to collect
interval = '1mo'


# tickers = investing_data.get_tickers(tickers)
# ohlc = investing_data.ohlc(tickers, years, interval)
piotroski = investing_strategy.piotroski(tickers)
# magic = investing_strategy.magic_formula(tickers)

'''
1. Function to scrape company data in a uniform way for current year, previous 2 years
2. Strategy scripts for Piotroski, magic formula, portfolio rebalance, etc.
3. Backtest Function to deploy strategies concurrently over the same timeframe
4. Function to compare results against S&P500 and graph
'''
