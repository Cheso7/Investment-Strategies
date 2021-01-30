"""
@author: Cheso7
"""
import pandas as pd

def most_shorted(stats_cy,tickers):
    pcnt_short_by_float = stats_cy.iloc[24]*100
    pcnt_short_outstanding = stats_cy.iloc[25]*100
    no_of_shorts = stats_cy.iloc[22]
    no_of_shares = stats_cy.iloc[19]
    no_shares_short_outstanding = no_of_shorts*pcnt_short_outstanding
    short_outstanding_ratio = (no_shares_short_outstanding/no_of_shares)*100 
    df_short = pd.DataFrame([pcnt_short_by_float, 
                            pcnt_short_outstanding, 
                            no_shares_short_outstanding, 
                            no_of_shares, short_outstanding_ratio], index = ['% Short by Float', 
                                                    '% Shorts Outstanding',
                                                    '# of Shorts Outstanding',
                                                    '# of Shares Floated',
                                                    'Short/Outstanding Ratio'])
    df_short_t = df_short.transpose()
    short_sorted = df_short_t.sort_values(by = 'Short/Outstanding Ratio', ascending=False)
    top10_shares_short = short_sorted[:10]
    print(top10_shares_short)

    return top10_shares_short

def piotroski(df_cy, df_py, df_py2, tickers):
    f_score = {}
    tickers = df_cy.columns
    
    for ticker in tickers:
        ROA_FS = int(df_cy.loc["Net income available to common shareholders",ticker]/((df_cy.loc["Total assets",ticker]+df_py.loc["Total assets",ticker])/2) > 0)
        CFO_FS = int(df_cy.loc["Net cash provided by operating activities",ticker] > 0)
        ROA_D_FS = int(df_cy.loc["Net income available to common shareholders",ticker]/(df_cy.loc["Total assets",ticker]+df_py.loc["Total assets",ticker])/2 > df_py.loc["Net income available to common shareholders",ticker]/(df_py.loc["Total assets",ticker]+df_py2.loc["Total assets",ticker])/2)
        CFO_ROA_FS = int(df_cy.loc["Net cash provided by operating activities",ticker]/df_cy.loc["Total assets",ticker] > df_cy.loc["Net income available to common shareholders",ticker]/((df_cy.loc["Total assets",ticker]+df_py.loc["Total assets",ticker])/2))
        LTD_FS = int((df_cy.loc["Long-term debt",ticker] + df_cy.loc["Other long-term liabilities",ticker])<(df_py.loc["Long-term debt",ticker] + df_py.loc["Other long-term liabilities",ticker]))
        CR_FS = int((df_cy.loc["Total current assets",ticker]/df_cy.loc["Total current liabilities",ticker])>(df_py.loc["Total current assets",ticker]/df_py.loc["Total current liabilities",ticker]))
        DILUTION_FS = int(df_cy.loc["Common stock",ticker] <= df_py.loc["Common stock",ticker])
        GM_FS = int((df_cy.loc["Gross profit",ticker]/df_cy.loc["Total revenue",ticker])>(df_py.loc["Gross profit",ticker]/df_py.loc["Total revenue",ticker]))
        ATO_FS = int(df_cy.loc["Total revenue",ticker]/((df_cy.loc["Total assets",ticker]+df_py.loc["Total assets",ticker])/2)>df_py.loc["Total revenue",ticker]/((df_py.loc["Total assets",ticker]+df_py2.loc["Total assets",ticker])/2))
        f_score[ticker] = [ROA_FS,CFO_FS,ROA_D_FS,CFO_ROA_FS,LTD_FS,CR_FS,DILUTION_FS,GM_FS,ATO_FS]
    f_score_df = pd.DataFrame(f_score,index=["PosROA","PosCFO","ROAChange","Accruals","Leverage","Liquidity","Dilution","GM","ATO"])
    f_score_sorted = f_score_df.sum().sort_values(ascending=False)
    
    return f_score_sorted

def magic_formula(df_cy, df_stats, tickers):

    all_stats_df = df_cy.append(df_stats)
    
    # calculating relevant financial metrics for each stock
    transpose_df = all_stats_df.transpose()
    final_stats_df = pd.DataFrame()
    final_stats_df["EBIT"] = transpose_df["EBITDA"] - transpose_df["Depreciation & amortisation"]
    final_stats_df["TEV"] =  transpose_df["Market cap (intra-day)"].fillna(0) \
                             +transpose_df["Long-term debt"].fillna(0) \
                             -(transpose_df["Total current assets"].fillna(0)-transpose_df["Total current liabilities"].fillna(0))
    final_stats_df["EarningYield"] =  final_stats_df["EBIT"]/final_stats_df["TEV"]
    final_stats_df["FCFYield"] = (transpose_df["Net cash provided by operating activities"]-transpose_df["Capital expenditure"])/transpose_df["Market cap (intra-day)"]
    final_stats_df["ROC"]  = (transpose_df["EBITDA"] - transpose_df["Depreciation & amortisation"])/(transpose_df["Net property, plant and equipment"]+transpose_df["Total current assets"]-transpose_df["Total current liabilities"])
    final_stats_df["BookToMkt"] = transpose_df["Total stockholders' equity"]/transpose_df["Market cap (intra-day)"]
    final_stats_df["Forward annual dividend yield"] = transpose_df["Forward annual dividend yield"]
    
    
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
    high_dividend_stocks = final_stats_df.sort_values("Forward annual dividend yield",ascending=False).iloc[:,6]
    print("------------------------------------------------")
    print("Highest dividend paying stocks")
    print(high_dividend_stocks)
    
    # # Magic Formula & Dividend yield combined
    final_stats_df["CombRank"] = final_stats_df["EarningYield"].rank(ascending=False,method='first') \
                                  +final_stats_df["ROC"].rank(ascending=False,method='first')  \
                                  +final_stats_df["Forward annual dividend yield"].rank(ascending=False,method='first')
    final_stats_df["CombinedRank"] = final_stats_df["CombRank"].rank(method='first')
    value_high_div_stocks = final_stats_df.sort_values("CombinedRank").iloc[:,[2,4,6,8]]
    print("------------------------------------------------")
    print("Magic Formula and Dividend Yield combined")
    print(value_high_div_stocks)
    
    return value_stocks