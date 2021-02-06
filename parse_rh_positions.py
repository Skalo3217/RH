import pandas as pd
import numpy as np
from yahoo_fin import stock_info
import robin_stocks as rs
import config
import os
import datetime
list4pandas = []
def profits(ticker):
    dfx = (df[df['symbol'] == ticker])
    dfxb = (dfx[dfx['side'].str.match('buy')]).copy()
    dfxb['each_trans'] = dfxb.quantity * dfxb.average_price
    buy_sum = dfxb.each_trans.sum()
    buy_quanity = dfxb.quantity.sum()
    b_average_price = buy_sum / buy_quanity
    dfxs = (dfx[dfx['side'].str.match('sell')]).copy()
    dfxs['each_trans'] = (dfxs.quantity * dfxs.average_price)
    sell_sum = dfxs.each_trans.sum() 
    sell_quanity = dfxs.quantity.sum()
    try:
        lastclose = stock_info.get_live_price(ticker)
    except Exception as e:
        print(e)
    if sell_quanity != 0:
        s_average_price = sell_sum / sell_quanity
    else:
        s_average_price = lastclose
    if sell_quanity >= buy_quanity:
        if s_average_price > 0:
            profit = sell_sum - buy_sum

        c_roi = roi(buy_sum,(s_average_price * sell_quanity))    
    elif sell_quanity <= buy_quanity:
        remaining_shares = buy_quanity - sell_quanity
        profit = s_average_price * sell_quanity
        if lastclose > 0:
            remaining_profit = lastclose * remaining_shares
        else:
            remaining_profit = b_average_price * remaining_shares
        if sell_quanity > 0:
            gain = profit + remaining_profit
            profit = gain + profit
            c_roi = roi(buy_sum,profit)
        else:
            profit = (buy_quanity * lastclose)
            c_roi = roi(buy_sum,profit)
        list4pandas.append([ticker, b_average_price, buy_quanity, s_average_price, sell_quanity, c_roi, profit])
        
def roi(invested,current):
    roi_final = (((current - invested) / invested) * 100)       
    return roi_final 

def download_csv():    
    try:    
        rs.login(username=config.RH_EMAIL,
                password=config.RH_PASS,
                expiresIn=86400,
                by_sms=True)
        os.chdir(config.DATA_PATH)
        rs.export_completed_stock_orders(".")
    except Exception as e:
        print('Failed to pull Robin Hood history')
        print(e)


monthdt = datetime.datetime.now()
month = monthdt.strftime("%b")
tday = datetime.date.today()
year = (tday.year)
day = (tday.day)
if day <= 9 :
    day = f"0{day}"
filelist = os.listdir(config.DATA_PATH)
filename = f'stock_orders_{month}-{day}-{year}.csv'
if filename not in filelist:
    download_csv()
else:
    try:
        df = pd.read_csv(f'data/{filename}')
        symbols = df['symbol'].tolist()
        symbols = list(dict.fromkeys(symbols))

    except Exception as e:
        print('Failed to open csv')
        print(e)

    i= 0
    for each in symbols:
        profits(each)
        i +=1

    df2 = pd.DataFrame(list4pandas,columns =['Symbol', 'Buy_Avg', 'Buy_Quanity', 'Sell_Avg', 'Sell_Quanity', '%_Change', 'Value'])
    df2.to_excel('robin_hood.xlsx')
