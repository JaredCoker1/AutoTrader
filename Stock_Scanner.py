# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 11:37:28 2021

@author: jared
"""
import pandas as pd
import time
import yfinance as yf
import json

def params():
    global listex
    global rsi_pick
    global sma_percent
    global portfolio
    global param_dict
    global previous_stocks
    param_dict = json.load(open('C:\\Users\\jared\\AutoTrader\\parameters.json'))
    listex = param_dict[0]['primary']['list']
    rsi_pick = param_dict[0]['primary']['rsi']
    sma_percent = param_dict[0]['primary']['percent']
    portfolio = param_dict[0]['primary']['portfolio']
    port = json.load(open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json'))
    previous_stocks = port[0]['INFO']['stocks']

def watchlist_reader():
    tic = time.perf_counter()
    watchlist_data = pd.read_csv("C:\\Users\\jared\\AutoTrader\\"+listex+".csv", skiprows=3) #reads the csv file exported from TOS
    matrix = watchlist_data[watchlist_data.columns[0]].to_numpy() #takes the first column of data (tickers) and puts it in its own matrix
    tickers = matrix.tolist() #converts matrix to a list ready for the remainder of code
    #very similar to the function list_len(), but this is used for grabbing data for calculations
    global low_sma
    low_sma = []
    global low_rsi
    low_rsi = []
    global good_rsi
    good_rsi = []
    global time_up
    time_up = [] #sets global variables so that other functions can access what is put into the lists
    print('You are about to look at '+ str(len(tickers)) + ' companies historical data.')
    time.sleep(1)
    #shutil.rmtree("C:\\users\\jared\\documents\\STONKS\\Data\\")#deletes old files
    #os.mkdir("C:\\users\\jared\\documents\\STONKS\\Data\\")#makes new folder for new files
    #load_bar = tqdm(total = num_comps)
    # This while loop is reponsible for storing the historical data for each ticker in our list. Note that yahoo finance sometimes incurs json.decode errors and because of this we are sleeping for 2 seconds after each iteration, also if a call fails we are going to try to execute it again. Also, do not make more than 2,000 calls per hour or 48,000 calls per day or Yahoo Finance may block your IP. The clause "(Amount_of_API_Calls < 1800)" below will stop the loop from making too many calls to the yfinance API.Prepare for this loop to take some time. It is pausing for 2 seconds after importing each stock.
    # Used to iterate through our list of tickers
    bad_grabs = 0
    j = []
    i=0
    while (i < len(tickers)): #loops through every ticker in the list that was selected
        try:
            stock = tickers[i]  # Gets the current stock ticker
            temp = yf.Ticker(str(stock)) # sets the stock to a yfinance object
            Hist_data = temp.history(period="1y") # grabs historical data for that stock
            #Hist_data.to_csv("C:\\users\\jared\\documents\\STONKS\\Data\\"+stock+".csv")  # Saves the historical data in csv format for further processing later
            #time.sleep(2)  # Pauses the loop for two seconds so we don't cause issues with Yahoo Finance's backend operations
            period = 20 # Set period length used in the calculations
            close_prices = close_grab(Hist_data) #puts the closing prices into a list
            mov_avg = moving_avg_calc(close_prices,period) #puts the sma into a variable
            rsi_val = rsi_calc(stock,close_prices,period)#puts the rsi into a variable
            rsi_prev = rsi_calc_prev(stock,close_prices,period)
            rsi_compare(stock,rsi_val,rsi_prev)
            time_compare(stock,close_prices) #checks whether or not the stock is up on the timeline or not
            compare_sma_to_price(stock,close_prices,mov_avg,period)
            bad_grabs = 0
            print(i)
            i += 1  # Iteration to the next ticker
        except ValueError:
            print("Error fetching data for "+str(stock)+"...")
            if bad_grabs > 3:
                i+=1
                j.append(str(stock)) # Some stocks dont have data, this allows the code to continue if there is a hiccup
            bad_grabs+=1
    toc = time.perf_counter()
    print("\nAll data loaded and calculated in " + str(round(toc-tic,2)) + " seconds.") 
    information() # calls the function to start the parameter calculations
    
def close_grab(Hist_data):
    load_matrix = Hist_data[Hist_data.columns[3]].to_numpy() #takes the first column of data (tickers) and puts it in its own matrix
    close_data = load_matrix.tolist() # function allows for quick access to the closing prices from the excel file
    return close_data

def moving_avg_calc(close_data, period):
    close_sum = 0
    i = 0
    if len(close_data)<period: # if there is not enough data to match the length of the period the SMA will not be calculated
        return "NULL"
    for i in range(0,period):
        close_sum+=int(close_data[len(close_data)-1-i]) 
    sma = close_sum/period # sums the closing prices for the length of the period then divides by the period to attain the SMA
    return sma

def compare_sma_to_price(stock,close_data,sma,period):
    if len(close_data)<period: # check to make sure the closing data is longer than the length
        return "NULL"
    last_close = float(close_data[len(close_data)-1])
    if last_close < sma:
        percent_off = float((sma-last_close))/sma*100 
        if percent_off > float(sma_percent):
            percent_off = round(percent_off,2) # compares current price to the SMA and calculates the difference, if it meets the inputed threshold its a good stock
            low_sma.append(stock) # adds worthy stocks to the low_sma list
            #return "Alert!\n\nThis stock has moved " + str(percent_off) + "% below the moving average."
    else:
        return "Problem comparing..."
    
def rsi_calc_prev(stock,close_data,period):
    if len(close_data)<period:
        return "NULL"
    i = period
    holding_price = 0.0
    tot_gain = 0.0
    tot_loss = 0.0
    while i>0:
        holding_price = float(close_data[len(close_data)-1-i-5])
        new_price = float(close_data[len(close_data)-1-i-4])
        holding_price = round(holding_price,2)
        new_price = round(new_price,2)
        i-=1
        diff = new_price-holding_price
        if diff > 0.0:
            gain = diff
            tot_gain+=gain
        elif diff < 0.0:
            loss = diff*(-1)
            tot_loss+=loss
    avg_gain = tot_gain/period
    avg_loss = tot_loss/period
    RSI_prev = 1000
    if avg_loss == 0:
        print("Tried to divide by zero...")
    else:
        RS = avg_gain/avg_loss
        RSI_prev = 100 - (100/(1+RS))
        RSI_prev = round(RSI_prev,2)

    return RSI_prev
    
def rsi_calc(stock,close_data,period):
    if len(close_data)<period:
        return "NULL"
    i = period
    holding_price = 0.0
    tot_gain = 0.0
    tot_loss = 0.0
    while i>0:
        holding_price = float(close_data[len(close_data)-1-i])
        new_price = float(close_data[len(close_data)-1-i+1])
        holding_price = round(holding_price,2)
        new_price = round(new_price,2)
        i-=1
        diff = new_price-holding_price
        if diff > 0.0:
            gain = diff
            tot_gain+=gain
        elif diff < 0.0:
            loss = diff*(-1)
            tot_loss+=loss
    avg_gain = tot_gain/period
    avg_loss = tot_loss/period
    RSI = 1000
    if avg_loss == 0:
        print("Tried to divide by zero...")
    else:
        RS = avg_gain/avg_loss
        RSI = 100 - (100/(1+RS))
        RSI = round(RSI,2)
        if RSI < rsi_pick:
            low_rsi.append(stock)
    return RSI
        
def rsi_compare(stock,rsi_val,rsi_prev):
    if rsi_val == 1000:
        return
    if rsi_prev <= rsi_val:
        good_rsi.append(stock)

def time_compare(stock,close_data):
    try:    
        init_price = float(close_data[0])
        last_price = float(close_data[len(close_data)-1])
        change = float((last_price-init_price)/init_price*100)
        if change >= 10.0: #compares first and last closing data
            time_up.append(stock)   #adds current stock to a year-up list, if not then it does nothing
    except IndexError:
        print("Index Error")            
def information():
    for i in low_rsi:
        if i in low_sma:
            if i in time_up:
                if i in good_rsi:#commented out for now bc theres not enough data
                    if i in previous_stocks:
                        continue
                    previous_stocks.append(i)
    data = json.load(open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json'))
    data[0]['INFO']['stocks'] = previous_stocks
    with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
        json.dump(data,outfile, indent = 4)
    print(previous_stocks)