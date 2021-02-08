'''
@author: Cheso7
TODO: If market cap = Null, drop data and do not write to DB.
TODO: Database OHLC data
'''
import investing_strategy
import data_collection
import investing_database
import pandas as pd

# Use this to run with chosen tickers
# tickers = ["AMD","TSLA", "AAPL", "GOOG", "AMZN"]

# Use this to import a list of tickers from an index on Wikipedia
tickers_list = 'http://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
tickers = data_collection.get_tickers(tickers_list)
table_name = 'snp'

# Use this to import tickers from an excel or CSV
# df = pd.read_excel('ASXTickers.xls')
# tickers = df['Tickers'].tolist()

# df = pd.read_csv('NYSE.txt', delimiter = '\t')
# tickers = df['Symbol'].tolist()

# Set parameters for OHLC Data
# years = 5 # years of data to collect
# interval = '1mo'

# Run this when the database needs to be created
# data_collection.get_financials(tickers, table_name)
# ohlc = data_collection.ohlc(tickers, years, interval)

def main():
    db_connection = investing_database.database_connect()
    Database = investing_database.Database(db_connection)

    statistics_dir_cy = Database.create_df_from_table(table_name+'_stats')
    stats_cy = statistics_dir_cy.set_index(statistics_dir_cy['Ticker'])
    stats_cy = stats_cy.transpose()
    stats_cy.drop('Ticker', inplace=True) 

    financial_dir_cy = Database.create_df_from_table(table_name + '_cy') 
    df_cy = financial_dir_cy.set_index(financial_dir_cy['Ticker'])  
    df_cy = df_cy.transpose()

    financial_dir_py = Database.create_df_from_table(table_name + '_py')
    df_py = financial_dir_py.set_index(financial_dir_py['Ticker'])   
    df_py = df_py.transpose()

    financial_dir_py2 = Database.create_df_from_table(table_name + '_py2')
    df_py2 = financial_dir_py2.set_index(financial_dir_py2['Ticker'])   
    df_py2 = df_py2.transpose()

    tickers = df_cy.columns

    piotroski = investing_strategy.piotroski(df_cy, df_py, df_py2,tickers)
    magic = investing_strategy.magic_formula(df_cy, stats_cy, tickers)
    shorted = investing_strategy.most_shorted(stats_cy, tickers)
    m_score = investing_strategy.m_score(df_cy, df_py,tickers)

    return

main()

