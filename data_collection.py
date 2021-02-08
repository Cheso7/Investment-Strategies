"""
@author: Cheso7
"""
import yfinance as yf
import datetime as dt
import copy
import bs4 as bs
import requests
import pandas as pd
import investing_database
import time

def get_tickers(tickers):
    if type(tickers) is not list:
    # Import all S&P500 Companies
        resp = requests.get(tickers)
        soup = bs.BeautifulSoup(resp.text, 'lxml')
        table = soup.find('table', {'class': 'wikitable sortable'})
        stock_list = []
        
        for row in table.findAll('tr')[1:]:
            ticker = row.findAll('td')[0].text
            stock_list.append(ticker)
        
        stock_list = [s.replace('\n', '') for s in stock_list]
        tickers = copy.deepcopy(stock_list)
    return tickers

def ohlc(tickers, years, interval):
    timespan = 365*years
    start = dt.datetime.today()-dt.timedelta(timespan)
    end = dt.datetime.today()    
    ohlc = {} 
    print('You are about to import data for', len(tickers), 'tickers')
    for ticker in tickers:
        ohlc[ticker] = yf.download(ticker,start,end,interval)
        ohlc[ticker].dropna(inplace=True,how="all")

    return ohlc

def get_financials(tickers, table_title):
    
    db_connection = investing_database.database_connect()
    Database = investing_database.Database(db_connection)
    index = 0
    for ticker in tickers:
        try:
            print('Scraping financial data for: ', ticker)
            temp_dir = {}
            temp_dir2 = {}
            temp_dir3 = {}

            #Getting balance sheet data from yahoo finance for the given ticker
            url = 'https://in.finance.yahoo.com/quote/'+ticker+'/balance-sheet?p='+ticker
            page = requests.get(url)
            page_content = page.content
            soup = bs.BeautifulSoup(page_content,'html.parser')
            tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})

            for t in tabl:
                rows = t.find_all("div", {"class" : "rw-expnded"})
                for row in rows:
                    temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[1]
                    temp_dir2[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[2]
                    temp_dir3[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[3]

            #Getting income statement data from yahoo finance for the given ticker
            url = 'https://in.finance.yahoo.com/quote/'+ticker+'/financials?p='+ticker
            page = requests.get(url)
            page_content = page.content
            soup = bs.BeautifulSoup(page_content,'html.parser')
            tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})

            for t in tabl:
                rows = t.find_all("div", {"class" : "rw-expnded"})
                for row in rows:
                    temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[2]
                    temp_dir2[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[3]
                    temp_dir3[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[4]

            #Getting cashflow statement data from yahoo finance for the given ticker
            url = 'https://in.finance.yahoo.com/quote/'+ticker+'/cash-flow?p='+ticker
            page = requests.get(url)
            page_content = page.content
            soup = bs.BeautifulSoup(page_content,'html.parser')
            tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})

            for t in tabl:
                rows = t.find_all("div", {"class" : "rw-expnded"})
                for row in rows:
                    temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[2]
                    temp_dir2[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[3]
                    temp_dir3[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[4]

            financial_dir_cy = pd.DataFrame(temp_dir, index=[index])
            financial_dir_cy_clean = info_filter_financials(financial_dir_cy, ticker)

            financial_dir_py = pd.DataFrame(temp_dir2, index=[index])  
            financial_dir_py_clean = info_filter_financials(financial_dir_py, ticker)

            financial_dir_py2 = pd.DataFrame(temp_dir3, index=[index])
            financial_dir_py2_clean = info_filter_financials(financial_dir_py2, ticker)

            Database.create_table_from_df(financial_dir_cy_clean, table_title + '_cy', 'Tickers')
            Database.create_table_from_df(financial_dir_py_clean, table_title + '_py', 'Tickers')
            Database.create_table_from_df(financial_dir_py2_clean, table_title + '_py2', 'Tickers')

            get_statistics(Database, ticker, table_title)
     
            index += 1 
            time.sleep(10)
        except:
            print('Problem scraping data for ', ticker)
    return

def get_statistics(Database, ticker, table_title):

        print('Scraping company statistics for: ', ticker)
        temp_dir ={}
        url = 'https://in.finance.yahoo.com/quote/'+ticker+'/key-statistics'
        page = requests.get(url)
        page_content = page.content
        soup = bs.BeautifulSoup(page_content,'html.parser')
        tabl = soup.findAll("table", {"class": "W(100%) Bdcl(c)"})

        for t in tabl:
            rows = t.find_all("tr")

            for row in rows:
                if len(row.get_text(separator='|').split("|")[0:2])>0:
                    temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[-1]

        ticker_statistics = pd.DataFrame(temp_dir, index = [ticker])
        ticker_statistics_clean = info_filter_stats(ticker_statistics, ticker)
        ticker_statistics['Ticker'] = ticker
        Database.create_table_from_df(ticker_statistics_clean, table_title + '_stats', 'Tickers')
        
def info_filter_stats(df, ticker):
    df.columns = df.columns.str.strip()
    df.columns.tolist() 
    df = df.replace({',': ''}, regex=True)
    df = df.replace({'N/A': float("NAN")}, regex=True)
    df = df.replace({'M': 'E+06'}, regex=True)
    df = df.replace({'B': 'E+09'}, regex=True)
    df = df.replace({'T': 'E+12'}, regex=True)
    df = df.replace({'%': 'E-02'}, regex=True)
    df = df.apply(pd.to_numeric, errors='coerce')
    df['Ticker'] = ticker
    return df

def info_filter_financials(df, ticker):
    df.columns = df.columns.str.strip()
    df.columns.tolist()
    df = df.replace({',': ''}, regex=True)
    df = df.replace({'N/A': float("NAN")}, regex=True)
    df = df.replace({'M': 'E+03'}, regex=True)
    df = df.replace({'B': 'E+06'}, regex=True)
    df = df.replace({'T': 'E+09'}, regex=True)
    df = df.replace({'%': 'E-02'}, regex=True)
    df = df.apply(pd.to_numeric, errors='coerce')
    df = df.multiply(1000)
    df['Ticker'] = ticker
    return df