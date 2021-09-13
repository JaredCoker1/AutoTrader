# -*- coding: utf-8 -*-
"""
Created on Wed Sep  1 15:21:06 2021

@author: jared
"""

import pandas as pd
import json
import math

def params():
    global listex
    global rsi_pick
    global sma_percent
    global portfolio
    global param_dict
    global previous_stocks
    global stocks
    global portfolio
    param_dict = json.load(open('C:\\Users\\jared\\AutoTrader\\parameters.json'))
    portfolio = param_dict[0]['primary']['portfolio']
    port = json.load(open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json'))
    stocks = port[0]['INFO']['stocks']
    listex = param_dict[0]['primary']['list']
    rsi_pick = param_dict[0]['primary']['rsi']
    sma_percent = param_dict[0]['primary']['percent']
    previous_stocks = port[0]['INFO']['stocks']
    print("RSI: "+str(rsi_pick))
    print("SMA: "+str(sma_percent))

def watchlist_reader():
    watchlist_data = pd.read_csv("C:\\Users\\jared\\AutoTrader\\"+listex+".csv", skiprows=3) #reads the csv file exported from TOS
    matrix = watchlist_data[watchlist_data.columns[0]].to_numpy() #takes the first column of data (tickers) and puts it in its own matrix
    tickers = matrix.tolist() 
    num_comps = len(tickers)
    print('You are about to look at '+ str(num_comps) + ' companies historical data.')
    global j
    global close_prices
    global period
    global low_sma
    global low_rsi
    global good_rsi
    global time_up
    good_rsi = []
    low_sma = []
    low_rsi = []
    time_up = []
    period=20
    j=period
    prices = pd.read_excel('result.xlsx',sheet_name=0,header=0,index_col=False)
    while (j < len(prices[tickers[0]])):#len(prices[tickers[0]])-period
        print("Day:"+str(j))
        s=0
        while s < 50: #should be the length of the ticker list
            stock = tickers[s]  # Gets the current stock ticker
            close_prices = prices[stock].tolist()
            mov_avg = moving_avg_calc(close_prices,period) #puts the sma into a variable
            rsi_val = rsi_calc(stock,close_prices,period)#puts the rsi into a variable
            rsi_prev = rsi_calc_prev(stock,close_prices,period)
            rsi_compare(stock,rsi_val,rsi_prev)
            time_compare(stock,close_prices) #checks whether or not the stock is up on the timeline or not
            compare_sma_to_price(stock,close_prices,mov_avg,period)
            information() # calls the function to start the parameter calculations
            numbers_update()
            reset()
            s+=1
        j+=1
# =============================================================================
#         print("GUD RSI: "+str(good_rsi))
#         print("LOW SMA: "+str(low_sma))
#         print("LOW RSI: "+str(low_rsi))
#         print("TYM  UP: "+str(time_up))
# =============================================================================
        good_rsi = []
        low_sma = []
        low_rsi = []
        time_up = []
        previous_stocks.clear()

def moving_avg_calc(close_data, period):
    close_sum = 0
    if len(close_data)<period: # if there is not enough data to match the length of the period the SMA will not be calculated
        print("bad")
        return "NULL"
    for p in range(0,period): #Loops through every day included in the period
        close_sum+=int(close_data[j-p]) #sums from end period to start period
    sma = close_sum/period # sums the closing prices for the length of the period then divides by the period to attain the SMA
    #print("SMA: "+str(sma))
    return sma

def compare_sma_to_price(stock,close_data,sma,period):
    if len(close_data)<period: # check to make sure the closing data is longer than the length
        return "NULL"
    last_close = float(close_data[j]) #the "last" day we are looking at depends on j index
    if last_close < sma:
        percent_off = float((sma-last_close))/sma*100 
        #print("Percent Off: "+str(percent_off))
        if percent_off > float(sma_percent):
            percent_off = round(percent_off,2) # compares current price to the SMA and calculates the difference, if it meets the inputed threshold its a good stock
            #print(percent_off)
            low_sma.append(stock) # adds worthy stocks to the low_sma list
    else:
        return "Problem comparing..."
    
def rsi_calc_prev(stock,close_data,period):
    if len(close_data)<period:
        return "NULL"
    i = period
    holding_price = 0.0
    tot_gain = 0.0
    tot_loss = 0.0
    q=0
    while i>0: #starts at the end of the period, works backwards
        q = period-i-4 #starts at 0 goes to period
        if q+j  <= len(close_data)-1: #cant go past the end of the list
            if q+j < 0:
                continue
            holding_price = float(close_data[j+q])
            new_price = float(close_data[j+q-1])
            holding_price = round(holding_price,2)
            new_price = round(new_price,2)
            diff = new_price-holding_price
            if diff > 0.0:
                gain = diff
                tot_gain+=gain
            elif diff < 0.0:
                loss = diff*(-1)
                tot_loss+=loss
        i-=1
    avg_gain = tot_gain/period
    avg_loss = tot_loss/period
    RSI_prev = 1000
    if avg_loss == 0:
        pass
    else:
        RS = avg_gain/avg_loss
        RSI_prev = 100 - (100/(1+RS))
        RSI_prev = round(RSI_prev,2)
    #print("RSI PREV: "+str(RSI_prev))
    return RSI_prev
    
def rsi_calc(stock,close_data,period):
    if len(close_data)<period:
        return "NULL"
    i = period
    holding_price = 0.0
    tot_gain = 0.0
    tot_loss = 0.0
    q=0
    while i>0:
        q=period-i
        if q+j <= len(close_data)-1:
            holding_price = float(close_data[j+q])
            new_price = float(close_data[j+q-1])
            holding_price = round(holding_price,2)
            new_price = round(new_price,2)
            diff = new_price-holding_price
            if diff > 0.0:
                gain = diff
                tot_gain+=gain
            elif diff < 0.0:
                loss = diff*(-1)
                tot_loss+=loss
        i=i-1
        
    avg_gain = tot_gain/period
    avg_loss = tot_loss/period
    RSI = 1000
    if avg_loss == 0:
        pass
    else:
        RS = avg_gain/avg_loss
        RSI = 100 - (100/(1+RS))
        RSI = round(RSI,2)
        if RSI < rsi_pick:
            low_rsi.append(stock)
    #print("RSI: "+str(RSI))
    return RSI
        
def rsi_compare(stock,rsi_val,rsi_prev):
    if rsi_val == 1000:
        return
    if rsi_prev <= rsi_val:
        good_rsi.append(stock)

def time_compare(stock,close_data):
    try:    
        init_price = float(close_data[0])
        last_price = float(close_data[j])  
    except IndexError:
        print("Index Error")
        #last_price = float(close_data[len(close_data)-1])
    change = float((last_price-init_price)/init_price*100)
    #print("Year change: "+str(change))
    if change >= 10.0:
        time_up.append(stock)
        
def information():    
    for i in low_rsi:
        if i in low_sma:
            if i in time_up:
                if i in good_rsi:
                    if i in previous_stocks:
                        continue
                    previous_stocks.append(i)
                    print(i+" is a buy")
    data = json.load(open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json'))
    data[0]['INFO']['stocks'] = previous_stocks
    with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
        json.dump(data,outfile, indent = 4)
    decisions()
    
def decisions():
    port = json.load(open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json'))
    cash = port[0]['INFO']['Cash']
    stocks = port[0]['INFO']['stocks']
    new_cash = cash
    useable_cash = 0.80*cash
    if useable_cash>=1000:
        useable_cash = 1000
    i = 0
    print(stocks)
    while (i < len(stocks)):
        stock = stocks[i]
        try:
            if port[i+1][stock]['status'] == "open" or port[i+1][stock]['status'] == "closed":
                i+=1
                continue
        except IndexError:
            pass
        except KeyError:
            print("Key Error")
            del port[0]['INFO'][stocks][i]
        last_price = close_prices[j]
        global exit_price
        exit_price = "null"
        num_shares = useable_cash/last_price
        num_shares = round(num_shares)
        holder = num_shares*last_price
        desired_value = useable_cash/len(stocks)
        while holder>=desired_value:
            num_shares-=1
            holder = num_shares*last_price
            if num_shares == 0:
                print("Stock too big for your portfolio")
        new_cash-=holder
        upload_dict = {
                str(stock):{
                "enter price" : round(last_price,3),
                "exit price" : exit_price,
                "status" : "open",
                "date in" : j+1,
                "date out" : "null",
                "shares" : num_shares,
                "value" : round(num_shares*last_price,3),
                "override": "null"
                }}
        print(stock+" bought at "+str(last_price))
        port[0]['INFO']['Cash'] = new_cash
        port.append(upload_dict)
        with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
            json.dump(port,outfile, indent = 4)
        i+=1

def numbers_update():
    port = json.load(open(r"C:\\Users\\jared\\AutoTrader\\"+portfolio+".json"))
    cash = port[0]['INFO']['Cash']
    stonks = port[0]['INFO']['stocks']
    i=1
    p_l = 0
    p_value = 0
    while i <= len(stonks):
        port = json.load(open(r"C:\\Users\\jared\\AutoTrader\\"+portfolio+".json"))
        cash = port[0]['INFO']['Cash']
        stonks = port[0]['INFO']['stocks']
        stock = stonks[i-1]
        if port[int(i)][stock]['status'] == "closed":
            del port[int(i)]
            del port[0]['INFO']['stocks'][i-1]
            with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
                json.dump(port,outfile, indent = 4)
            continue
        shares = port[int(i)][stock]['shares']
        if shares == 0:
            del port[int(i)]
            del port[0]['INFO']['stocks'][i-1]
            with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
                json.dump(port,outfile, indent = 4)
            continue
        original_value = port[int(i)][stock]['enter price']*shares
        if close_prices == []:
            print("Cannot update this stock value right now.")
            i+=1
            continue
        last_price = close_prices[len(close_prices)-1]
        new_value = shares*last_price
        p_value+=new_value
        port[int(i)][stock]['value'] = new_value
        hold = round(new_value,2)-round(original_value,2)
        p_l += hold
        port[int(i)][stock]['p/l'] = hold
        i+=1
    p_value += cash
    p_value = round(p_value,2)
    cash = round(cash,2)
    port[0]['INFO']['Portfolio Value'] = p_value
    with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
        json.dump(port,outfile, indent = 4)
    check_sell()

def check_sell():
    port = json.load(open(r"C:\\Users\\jared\\AutoTrader\\"+portfolio+".json"))
    cash = port[0]['INFO']['Cash']
    stonks = port[0]['INFO']['stocks']
    i=1
    p_l = 0
    p_value = 0
    while i <= len(stonks):
        stock = stonks[i-1]
        shares = port[int(i)][stock]['shares']
        original_value = port[int(i)][stock]['enter price']*shares
        original_value = round(original_value,2)
        if port[int(i)][stock]['status'] == "closed":
            i+=1
            continue
        if close_prices == []:
            print("Cannot update this stock value right now.")
            i+=1
            continue
        last_price = close_prices[len(close_prices)-1]
        new_value = round(shares*last_price,2)
        p_value+=new_value
        if original_value == 0.0:
            print("Cannot execute...No shares owned")
            p_change = 0.0
        else:
            p_change = (new_value-original_value)/original_value
        if p_change < -0.03:
            port[int(i)][stock]['status'] = "to close"
        if p_change >= 0:
            if p_change >=0.015:
                port[int(i)][stock]['status'] = "to close"  
        else:
            pass
        hold = round(new_value,2)-round(original_value,2)
        p_l += hold
        i+=1
    p_value += cash
    cash = round(cash,2)
    port[0]['INFO']['Portfolio Value'] = round(p_value,2)
    with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
        json.dump(port,outfile, indent = 4)
    sell_conf()    

def sell_conf():
    port = json.load(open(r"C:\\Users\\jared\\AutoTrader\\"+portfolio+".json"))
    cash = port[0]['INFO']['Cash']
    stonks = port[0]['INFO']['stocks']
    i=1
    while i <= len(stonks):
        stock = stonks[i-1]
        if port[int(i)][stock]['status'] == "to close" or port[int(i)][stock]['override']=="sell":
            last_price = close_prices[len(close_prices)-1]
            port[int(i)][stock]['exit price'] = round(last_price,2)
            print(str(stock)+" sold at "+str(round(last_price,2)))
            cash+= port[int(i)][stock]['value']
            port[int(i)][stock]['date out'] = j
            pl = round(last_price-port[int(i)][stock]['enter price'],2)
            port[int(i)][stock]['p/l'] = pl
            port[int(i)][stock]['status'] = "closed"
        i+=1   
    port[0]['INFO']['Cash'] = round(cash,2)
    with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
        json.dump(port,outfile, indent = 4)
    
def reset():
    port = json.load(open(r"C:\\Users\\jared\\AutoTrader\\"+portfolio+".json"))
    stonks = port[0]['INFO']['stocks']
    cash = port[0]['INFO']['Cash']
    val = port[0]['INFO']['Portfolio Value']
    i=1
    while i <= len(stonks):
        stock = stonks[i-1]
        if j == len(close_prices)-period-1:
            last_price = close_prices[len(close_prices)-1]
            port[int(i)][stock]['exit price'] = round(last_price,2)
            #print(stock+" forced sold at "+str(round(last_price,2)))
            cash+= port[int(i)][stock]['value']
            port[int(i)][stock]['date out'] = j
            pl = round(last_price-port[int(i)][stock]['enter price'],2)
            port[int(i)][stock]['p/l'] = pl
            port[int(i)][stock]['status'] = "closed"
            port[0]['INFO']['Cash'] = round(cash,2)
            port[0]['INFO']['History'].append(port[0]['INFO']['Portfolio Value']) 
            with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
                json.dump(port,outfile, indent = 4)
        i+=1
    port = json.load(open(r"C:\\Users\\jared\\AutoTrader\\"+portfolio+".json"))
    stonks = port[0]['INFO']['stocks']
    cash = port[0]['INFO']['Cash']
    i=1
    while i <= len(stonks):
        stock = stonks[i-1]
        try:
            if port[int(i)][stock]['status'] == "closed":
                del port[int(i)]
                del stonks[i-1]
        except KeyError:
            print("key error")
        except IndexError:
            print("index problem")
        i+=1
    port[0]['INFO']['stocks'] = []
    with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
        json.dump(port,outfile, indent = 4)

params()
watchlist_reader()
