# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 12:04:20 2021

@author: jches
"""
import pandas as pd
import investing_data

def piotroski(tickers):
# selecting relevant financial information for each stock using fundamental data
    stats = ["Net income available to common shareholders",
             "Total assets",
             "Net cash provided by operating activities",
             "Long-term debt",
             "Other long-term liabilities",
             "Total current assets",
             "Total current liabilities",
             "Common stock",
             "Total revenue",
             "Gross profit"] # change as required
    
    indx = ["NetIncome","TotAssets","CashFlowOps","LTDebt","OtherLTDebt",
            "CurrAssets","CurrLiab","CommStock","TotRevenue","GrossProfit"]

    combined_financials_cy = investing_data.financials(tickers, 1)
    combined_financials_py = investing_data.financials(tickers, 2)
    combined_financials_py2 = investing_data.financials(tickers, 3)

    
    df_cy = investing_data.info_filter(combined_financials_cy, stats, indx)
    df_py = investing_data.info_filter(combined_financials_py, stats, indx)
    df_py2 = investing_data.info_filter(combined_financials_py2, stats, indx)
    
    f_score = {}
    tickers = df_cy.columns
    
    for ticker in tickers:
        ROA_FS = int(df_cy.loc["NetIncome",ticker]/((df_cy.loc["TotAssets",ticker]+df_py.loc["TotAssets",ticker])/2) > 0)
        CFO_FS = int(df_cy.loc["CashFlowOps",ticker] > 0)
        ROA_D_FS = int(df_cy.loc["NetIncome",ticker]/(df_cy.loc["TotAssets",ticker]+df_py.loc["TotAssets",ticker])/2 > df_py.loc["NetIncome",ticker]/(df_py.loc["TotAssets",ticker]+df_py2.loc["TotAssets",ticker])/2)
        CFO_ROA_FS = int(df_cy.loc["CashFlowOps",ticker]/df_cy.loc["TotAssets",ticker] > df_cy.loc["NetIncome",ticker]/((df_cy.loc["TotAssets",ticker]+df_py.loc["TotAssets",ticker])/2))
        LTD_FS = int((df_cy.loc["LTDebt",ticker] + df_cy.loc["OtherLTDebt",ticker])<(df_py.loc["LTDebt",ticker] + df_py.loc["OtherLTDebt",ticker]))
        CR_FS = int((df_cy.loc["CurrAssets",ticker]/df_cy.loc["CurrLiab",ticker])>(df_py.loc["CurrAssets",ticker]/df_py.loc["CurrLiab",ticker]))
        DILUTION_FS = int(df_cy.loc["CommStock",ticker] <= df_py.loc["CommStock",ticker])
        GM_FS = int((df_cy.loc["GrossProfit",ticker]/df_cy.loc["TotRevenue",ticker])>(df_py.loc["GrossProfit",ticker]/df_py.loc["TotRevenue",ticker]))
        ATO_FS = int(df_cy.loc["TotRevenue",ticker]/((df_cy.loc["TotAssets",ticker]+df_py.loc["TotAssets",ticker])/2)>df_py.loc["TotRevenue",ticker]/((df_py.loc["TotAssets",ticker]+df_py2.loc["TotAssets",ticker])/2))
        f_score[ticker] = [ROA_FS,CFO_FS,ROA_D_FS,CFO_ROA_FS,LTD_FS,CR_FS,DILUTION_FS,GM_FS,ATO_FS]
    f_score_df = pd.DataFrame(f_score,index=["PosROA","PosCFO","ROAChange","Accruals","Leverage","Liquidity","Dilution","GM","ATO"])
    f_score_sorted = f_score_df.sum().sort_values(ascending=False)
    
    return f_score_sorted

def magic_formula(tickers):
    stats = ["EBITDA",
          "Depreciation & amortisation",
          "Market Cap (intraday)",
          "Net income available to common shareholders",
          "Net cash provided by operating activities",
          "Capital expenditure",
          "Total current assets",
          "Total current liabilities",
          "Net property, plant and equipment",
          "Total stockholders' equity",
          "Long-term debt",
          "Forward Annual Dividend Yield"] # change as required
    
    indx = ["EBITDA","D&A","MarketCap","NetIncome","CashFlowOps","Capex","CurrAsset",
         "CurrLiab","PPE","BookValue","TotDebt","DivYield"] 
     
    combined_financials_cy = investing_data.financials(tickers, 1)
    combined_financials_cy_dropped = combined_financials_cy.drop("EBITDA")
    statistics = investing_data.statistics(tickers)
    
    all_stats_df = combined_financials_cy_dropped.append(statistics)
    all_stats_df = investing_data.info_filter(all_stats_df, stats, indx)
    
    # calculating relevant financial metrics for each stock
    transpose_df = all_stats_df.transpose()
    final_stats_df = pd.DataFrame()
    final_stats_df["EBIT"] = transpose_df["EBITDA"] - transpose_df["D&A"]
    final_stats_df["TEV"] =  transpose_df["MarketCap"].fillna(0) \
                             +transpose_df["TotDebt"].fillna(0) \
                             -(transpose_df["CurrAsset"].fillna(0)-transpose_df["CurrLiab"].fillna(0))
    final_stats_df["EarningYield"] =  final_stats_df["EBIT"]/final_stats_df["TEV"]
    final_stats_df["FCFYield"] = (transpose_df["CashFlowOps"]-transpose_df["Capex"])/transpose_df["MarketCap"]
    final_stats_df["ROC"]  = (transpose_df["EBITDA"] - transpose_df["D&A"])/(transpose_df["PPE"]+transpose_df["CurrAsset"]-transpose_df["CurrLiab"])
    final_stats_df["BookToMkt"] = transpose_df["BookValue"]/transpose_df["MarketCap"]
    final_stats_df["DivYield"] = transpose_df["DivYield"]
    
    
    ################################Output Dataframes##############################
    
    # finding value stocks based on Magic Formula
    final_stats_val_df = final_stats_df.loc[tickers,:]
    final_stats_val_df["CombRank"] = final_stats_val_df["EarningYield"].rank(ascending=False,na_option='bottom')+final_stats_val_df["ROC"].rank(ascending=False,na_option='bottom')
    final_stats_val_df["MagicFormulaRank"] = final_stats_val_df["CombRank"].rank(method='first')
    value_stocks = final_stats_val_df.sort_values("MagicFormulaRank").iloc[:,[2,4,8]]
    print("------------------------------------------------")
    print("Value stocks based on Greenblatt's Magic Formula")
    print(value_stocks)
    
    # finding highest dividend yield stocks
    high_dividend_stocks = final_stats_df.sort_values("DivYield",ascending=False).iloc[:,6]
    print("------------------------------------------------")
    print("Highest dividend paying stocks")
    print(high_dividend_stocks)
    
    # # Magic Formula & Dividend yield combined
    final_stats_df["CombRank"] = final_stats_df["EarningYield"].rank(ascending=False,method='first') \
                                  +final_stats_df["ROC"].rank(ascending=False,method='first')  \
                                  +final_stats_df["DivYield"].rank(ascending=False,method='first')
    final_stats_df["CombinedRank"] = final_stats_df["CombRank"].rank(method='first')
    value_high_div_stocks = final_stats_df.sort_values("CombinedRank").iloc[:,[2,4,6,8]]
    print("------------------------------------------------")
    print("Magic Formula and Dividend Yield combined")
    print(value_high_div_stocks)
    
    return value_stocks