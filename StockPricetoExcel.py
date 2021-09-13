# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 18:09:17 2021

@author: jared
"""
import pandas as pd
import yfinance as yf
from tqdm import tqdm
import time

watchlist_data = pd.read_csv("C:\\Users\\jared\\AutoTrader\\NYSE.csv", skiprows=3) #reads the csv file exported from TOS
matrix = watchlist_data[watchlist_data.columns[0]].to_numpy() #takes the first column of data (tickers) and puts it in its own matrix
tickers = matrix.tolist()
df = pd.DataFrame()
progress = tqdm(total=len(tickers))

hist_data = yf.Ticker(tickers[0]).history(period="ytd")
load_matrix = hist_data[hist_data.columns[0]].to_numpy()
dates = load_matrix.tolist()
length = len(dates)
col1 = list(range(length))
df[0] = pd.Series(col1)
i=0

while i < len(tickers):
    progress.update(1)
    time.sleep(0.05)
    hist_data = yf.Ticker(tickers[i]).history(period="ytd")
    load_matrix = hist_data[hist_data.columns[3]]
    diff = len(col1)-len(load_matrix)
    if diff !=0:
        print("Adding Zeros")
        print("Should have "+str(len(col1))+" days, but only has "+str(len(load_matrix))+" days.")
        for j in range(0,diff):
            load_matrix = pd.Series([0]).append(load_matrix,ignore_index=True)
    load_matrix = load_matrix.to_numpy().tolist()
    df[tickers[i]] = pd.Series(load_matrix)
   # df = pd.concat([df,load_matrix])
    i+=1

df.to_excel('result.xlsx', index = False)