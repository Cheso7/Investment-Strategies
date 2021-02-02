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

def get_financials(tickers):
    financial_dir_cy = {} #directory to store current year's information
    financial_dir_py = {} #directory to store last year's information
    financial_dir_py2 = {}

    for ticker in tickers:
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
        
        financial_dir_cy[ticker] = temp_dir
        financial_dir_py[ticker] = temp_dir2
        financial_dir_py2[ticker] = temp_dir3

    financials_cy = pd.DataFrame(financial_dir_cy)
    financials_py = pd.DataFrame(financial_dir_py)
    financials_py2 = pd.DataFrame(financial_dir_py2)

    return financials_cy, financials_py, financials_py2

def get_statistics(tickers):

    db_connection = investing_database.database_connect()
    Database = investing_database.Database(db_connection)
    
    for ticker in tickers:
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
        ticker_statistics_clean = info_filter_stats(ticker_statistics)
        Database.create_table_from_df(ticker_statistics_clean,'companystats')

    return 

def info_filter_stats(df):

    df = df.replace({',': ''}, regex=True)
    df = df.replace({'M': 'E+06'}, regex=True)
    df = df.replace({'B': 'E+09'}, regex=True)
    df = df.replace({'T': 'E+12'}, regex=True)
    df = df.replace({'%': 'E-02'}, regex=True)
    df = df.apply(pd.to_numeric, errors='ignore')
    
    return df

def info_filter_financials(df):
    tickers = df.index.tolist()
    df[tickers] = df[tickers].replace({',': ''}, regex=True)
    df[tickers] = df[tickers].replace({'M': 'E+03'}, regex=True)
    df[tickers] = df[tickers].replace({'B': 'E+06'}, regex=True)
    df[tickers] = df[tickers].replace({'T': 'E+9'}, regex=True)
    df[tickers] = df[tickers].replace({'%': 'E-02'}, regex=True)  

    for ticker in df.columns:
        df[ticker] = pd.to_numeric(df[ticker].values,errors='coerce')
        df[ticker] = df[ticker].multiply(1000)
    tickers = df.columns      
    return df

    
# financials_stats =  ["Total revenue",
#                     "Cost of revenue",
#                     "Gross profit",
#                     "Research development",
#                     "Selling general and administrative",
#                     "Total operating expenses",
#                     "Operating income or loss",
#                     "Interest expense",
#                     "Total other income/expenses net",
#                     "Income before tax",
#                     "Income tax expense",
#                     "Income from continuing operations",
#                     "Net income",
#                     "Net income available to common shareholders",
#                     "Basic EPS",
#                     "Diluted EPS",
#                     "Basic average shares",
#                     "Diluted average shares",
#                     "EBITDA",
#                     "Cash and cash equivalents",
#                     "Other short-term investments",
#                     "Total cash",
#                     "Net receivables",
#                     "Inventory",
#                     "Other current assets",
#                     "Total current assets",
#                     "Gross property, plant and equipment",
#                     "Accumulated depreciation",
#                     "Net property, plant and equipment",
#                     "Equity and other investments",
#                     "Goodwill",
#                     "Intangible assets",
#                     "Other long-term assets",
#                     "Total non-current assets",
#                     "Total assets",
#                     "Current debt",
#                     "Accounts payable",
#                     "Accrued liabilities",
#                     "Deferred revenues",
#                     "Other current liabilities",
#                     "Total current liabilities",
#                     "Long-term debt",
#                     "Deferred tax liabilities",
#                     "Deferred revenues",
#                     "Other long-term liabilities",
#                     "Total non-current liabilities",
#                     "Total liabilities",
#                     "Common stock",
#                     "Retained earnings",
#                     "Accumulated other comprehensive income",
#                     "Total stockholders' equity",
#                     "Total liabilities and stockholders' equity",
#                     "Net income",
#                     "Depreciation & amortisation",
#                     "Deferred income taxes",
#                     "Stock-based compensation",
#                     "Change in working capital",
#                     "Accounts receivable",
#                     "Inventory",
#                     "Accounts payable",
#                     "Other working capital",
#                     "Other non-cash items",
#                     "Investments in property, plant and equipment",
#                     "Acquisitions, net",
#                     "Purchases of investments",
#                     "Sales/maturities of investments",
#                     "Other investing activities",
#                     "Net cash used for investing activities",
#                     "Debt repayment",
#                     "Common stock issued",
#                     "Common stock repurchased",
#                     "Dividends paid",
#                     "Other financing activities",
#                     "Net cash used provided by (used for) financing activities",
#                     "Net change in cash",
#                     "Cash at beginning of period",
#                     "Cash at end of period",
#                     "Operating cash flow",
#                     "Capital expenditure",
#                     "Free cash flow"]

# statistics_stats = ['Market cap (intra-day)',
#                     'Enterprise value',
#                     'Trailing P/E',
#                     'Forward P/E',
#                     'PEG Ratio (5 yr expected)',
#                     'Price/sales (ttm)',
#                     'Price/book (mrq)',
#                     'Enterprise value/revenue',
#                     'Enterprise value/EBITDA',
#                     'Beta (5Y monthly)',
#                     '52-week change',
#                     'S&P500 52-week change',
#                     '52-week high',
#                     '52-week low',
#                     '50-day moving average',
#                     '200-day moving average',
#                     'Avg vol (3-month)',
#                     'Avg vol (10-day)',
#                     'Shares outstanding',
#                     'Float',
#                     'Percent held by insiders',
#                     'Percent held by institutions',
#                     'Shares short',
#                     'Short ratio',
#                     'Short percent of float',
#                     'Short percent of shares outstanding',
#                     'Shares short prior month',
#                     'Forward annual dividend rate',
#                     'Forward annual dividend yield',
#                     'Trailing annual dividend rate',
#                     'Trailing annual dividend yield',
#                     '5-year average dividend yield ',
#                     'Payout ratio',
#                     'Dividend date',
#                     'Ex-dividend date',
#                     'Last split factor',
#                     'Last split date',
#                     'Fiscal year ends',
#                     'Most-recent quarter',
#                     'Profit margin',
#                     'Operating margin',
#                     'Return on assets',
#                     'Return on equity',
#                     'Revenue',
#                     'Revenue per share',
#                     'Quarterly revenue growth',
#                     'Gross profit',
#                     'EBITDA',
#                     'Net income avi to common',
#                     'Diluted EPS',
#                     'Quarterly earnings growth',
#                     'Total cash',
#                     'Total cash per share',
#                     'Total debt',
#                     'Total debt/equity',
#                     'Current ratio',
#                     'Book value per share',
#                     'Operating cash flow',
#                     'Levered free cash flow']


