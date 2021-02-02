'''
@author: Cheso7
TODO: Fix bug with regards to storing first row of SQL Table.
TODO: Add SQL table storage for other data collection functions
TODO: Check magnitude of info_filter for financial data
TODO: Check investing functions work with SQL Data table imported
'''
import investing_strategy
import data_collection
import investing_database
import pandas as pd

#Use this to run with chosen tickers
tickers = ["AMD","NVDA"]

#Use this to import a list of tickers from an index on Wikipedia
# tickers_list = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
# tickers = data_collection.get_tickers(tickers_list)

# df = pd.read_excel('NASDAQTIckers.xls')
# tickers = df['Tickers'].tolist()

#Parameters
years = 5 # years of data to collect
interval = '1mo'

data_collection.get_statistics(tickers)

def main():
    db_connection = investing_database.database_connect()
    Database = investing_database.Database(db_connection)
    # ohlc = data_collection.ohlc(tickers, years, interval)
    # financials_cy, financials_py, financials_py2 = data_collection.get_financials(tickers)
    statistics_dir_cy = Database.create_df_from_table('companystats')   

    # df_cy = data_collection.info_filter_financials(financials_cy)
    # df_py = data_collection.info_filter_financials(financials_py)
    # dy_py2 = data_collection.info_filter_financials(financials_py2)
    # stats_cy = data_collection.info_filter_stats(statistics_dir_cy)

    # piotroski = investing_strategy.piotroski(df_cy, df_py, dy_py2,tickers)
    # magic = investing_strategy.magic_formula(df_cy, stats_cy, tickers)
    shorted = investing_strategy.most_shorted(statistics_dir_cy, tickers)
    return

main()

