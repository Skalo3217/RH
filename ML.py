import pandas as pd
from pandas_datareader import data
import numpy as np
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import config
import os
import datetime

def filename():
    monthdt = datetime.datetime.now()
    month = monthdt.strftime("%b")
    tday = datetime.date.today()
    year = (tday.year)
    day = (tday.day)
    if day <= 9 :
        day = f"0{day}"
    return f'stock_orders_{month}-{day}-{year}.csv'

def file_name_const(): # yyyymmdd
    monthdt = datetime.datetime.now()
    tday = datetime.date.today()
    year = (tday.year)
    day = (tday.day)
    if day <= 9 :
        day = f"0{day}"
    month = tday.month
    if month <= 9:
        month = f"0{month}"
    return f"{year}{month}{day}"


def get_data(stock):
    start = "01-01-2013"
    df=data.DataReader(stock, "yahoo", start=start)
    df.to_csv(f"data/{stock}_{temp}.csv")


try:
    filename = filename()
    df = pd.read_csv(f'data/{filename}')
    symbols = df['symbol'].tolist()
    symbols = list(dict.fromkeys(symbols))
except Exception as e:
    print('Failed to open csv')
    print(e)

gain_stock_predictions = []
loss_stock_predictions =[]

temp = file_name_const()
i= 0
for each in symbols:
    tickers =[]
    print(each)
    get_data(each)
    df = pd.read_csv(f"data/{each}_{temp}.csv", index_col=0)
    df['HL_pct'] = (df['High']-df['Low']) / df['Low'] * 100
    df=df[['Adj Close', 'Volume', 'HL_pct']]
    predict_col = 'Adj Close'
    df.fillna(0, inplace=True)
    df['future5days'] = df[predict_col].shift(-5)
    df.dropna(inplace=True)

    X = np.array(df.drop(['future5days'],1))
    X = preprocessing.scale(X)
    y = np.array(df['future5days'])

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3)

    clf = LinearRegression()
    clf.fit(X_train, y_train)

    confidence = clf.score(X_train, y_train)
    print("Accuracy:", confidence)

    df_test = pd.read_csv(f"data/{each}_{temp}.csv", index_col=0)

    df_test['HL_pct'] = (df_test['High']-df_test['Low']) /df_test['Low'] * 100
    df_test=df_test[['Adj Close', 'Volume', 'HL_pct']]

    X_new = np.array(df_test)
    X_new = preprocessing.scale(X_new)


    for x in (X_new):
        tickers.append(clf.predict([x])[0])
    record_count = (len(tickers)-5)
    five_day_prediction = (tickers[record_count:])
    day1=five_day_prediction[-1]
    day2=five_day_prediction[-2]
    day3=five_day_prediction[-3]
    day4=five_day_prediction[-4]
    day5=five_day_prediction[-5]
    if day1 < day5:        
        gain_stock_predictions.append([each,confidence,day1,day2,day3,day4,day5])
    else:
        loss_stock_predictions.append([each,confidence,day1,day2,day3,day4,day5])
    i +=1
dfgain = pd.DataFrame(gain_stock_predictions)
dfgain.to_excel(f'gain_pred_{file_name_const()}.xlsx')
dfloss = pd.DataFrame(loss_stock_predictions)
dfloss.to_excel(f'loss_pred_{file_name_const()}.xlsx')