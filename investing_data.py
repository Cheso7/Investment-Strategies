# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 10:01:34 2021

@author: Cheso7
"""

import yfinance as yf
import datetime as dt
import copy
import bs4 as bs
import requests
import pandas as pd

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
    ohlc = {} # dictionary to store ohlc value for each stock 
    # Download historical data (monthly) for stocks
    print('You are about to import data for', len(tickers), 'tickers')
    
    # looping over tickers and creating a dataframe with close prices
    for ticker in tickers:
        ohlc[ticker] = yf.download(ticker,start,end,interval)
        ohlc[ticker].dropna(inplace=True,how="all")

    return ohlc


def financials(tickers, fin_year):
    financial_data = {}
    for ticker in tickers:
        if fin_year == 1:
            print("Scraping current financial year statement for ", ticker)
        elif fin_year == 2:
            print("Scraping -1 year financial year statement for ", ticker)
        elif fin_year == 3:
            print("Scraping -2 year financial year statement for ", ticker)
       
        temp_dir = {}
        try:

            
            #Getting balance sheet data from yahoo finance for the given ticker
            url = 'https://in.finance.yahoo.com/quote/'+ticker+'/balance-sheet?p='+ticker
            page = requests.get(url)
            page_content = page.content
            soup = bs.BeautifulSoup(page_content,'html.parser')
            tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})
            for t in tabl:
                rows = t.find_all("div", {"class" : "rw-expnded"})
                for row in rows:
                    temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[fin_year]
    
            #Getting income statement data from yahoo finance for the given ticker
            url = 'https://in.finance.yahoo.com/quote/'+ticker+'/financials?p='+ticker
            page = requests.get(url)
            page_content = page.content
            soup = bs.BeautifulSoup(page_content,'html.parser')
            tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})
            for t in tabl:
                rows = t.find_all("div", {"class" : "rw-expnded"})
                for row in rows:
                    temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[fin_year]
    
            #Getting cashflow statement data from yahoo finance for the given ticker
            url = 'https://in.finance.yahoo.com/quote/'+ticker+'/cash-flow?p='+ticker
            page = requests.get(url)
            page_content = page.content
            soup = bs.BeautifulSoup(page_content,'html.parser')
            tabl = soup.find_all("div", {"class" : "M(0) Whs(n) BdEnd Bdc($seperatorColor) D(itb)"})
            for t in tabl:
                rows = t.find_all("div", {"class" : "rw-expnded"})
                for row in rows:
                    temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[fin_year]
                        
            #Combining all extracted information with the corresponding ticker
            
            financial_data[ticker] = temp_dir
        except:
            print("Problem scraping data for ",ticker)
        
    combined_financials = pd.DataFrame(financial_data)
    combined_financials.dropna(how='all',axis=1,inplace=True) #dropping columns with all NaN values
    tickers = combined_financials.columns #updating the tickers list based on only those tickers whose values were successfully extracted
        
    for ticker in tickers:
        combined_financials = combined_financials[~combined_financials[ticker].str.contains("[a-z]").fillna(False)]
        return combined_financials

def statistics(tickers):
    financial_data = {}
    
    for ticker in tickers:
        temp_dir ={}
        #Getting key statistics data from yahoo finance for the given ticker
        url = 'https://finance.yahoo.com/quote/'+ticker+'/key-statistics'
        page = requests.get(url)
        page_content = page.content
        soup = bs.BeautifulSoup(page_content,'html.parser')
        tabl = soup.findAll("table") # try soup.findAll("table") if this line gives error 
        for t in tabl:
            rows = t.find_all("tr")
            for row in rows:
                if len(row.get_text(separator='|').split("|")[0:2])>0:
                    temp_dir[row.get_text(separator='|').split("|")[0]]=row.get_text(separator='|').split("|")[-1]
        financial_data[ticker] = temp_dir
        
    statistics = pd.DataFrame(financial_data)
    return statistics
    
def info_filter(df,stats,indx):
    """function to filter relevant financial information for each 
       stock and transforming string inputs to numeric"""
    tickers = df.columns
    all_stats = {}
    
    for ticker in tickers:
        try:
            temp = df[ticker]
            ticker_stats = []
            for stat in stats:
                ticker_stats.append(temp.loc[stat])
            all_stats['{}'.format(ticker)] = ticker_stats
        except:
            print("can't read data for ",ticker)
            
    all_stats_df = pd.DataFrame(all_stats,index=indx)
    all_stats_df[tickers] = all_stats_df[tickers].replace({',': ''}, regex=True)
    all_stats_df[tickers] = all_stats_df[tickers].replace({'M': 'E+03'}, regex=True)
    all_stats_df[tickers] = all_stats_df[tickers].replace({'B': 'E+06'}, regex=True)
    all_stats_df[tickers] = all_stats_df[tickers].replace({'T': 'E+09'}, regex=True)
    all_stats_df[tickers] = all_stats_df[tickers].replace({'%': 'E-02'}, regex=True)
    for ticker in all_stats_df.columns:
        all_stats_df[ticker] = pd.to_numeric(all_stats_df[ticker].values,errors='coerce')
    # all_stats_df.dropna(axis=1,inplace=True)
    tickers = all_stats_df.columns      
    return all_stats_df