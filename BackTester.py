# -*- coding: utf-8 -*-
"""
Created on Fri May  7 00:45:36 2021

@author: jared
"""

import robin_stocks.robinhood as r
import yfinance as yf
import pandas as pd
import time
import json
from datetime import date

login = r.login('***************','***************')

# =============================================================================
# my_stocks = r.build_holdings()
# my_profile = r.build_user_profile()
# print("Portfolio Value: $"+my_profile['equity'])
# print("Portfolio Cash:  $"+my_profile['cash'])
# print("Stocks Owned: ")
# for key,value in my_stocks.items():
#     print(key)
# stock = r.stocks.get_stock_quote_by_symbol("AAPL",info = None)
# print(stock['last_trade_price'])
# #r.order_sell_market('WRAP',1)
# =============================================================================
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
    
def close_grab(Hist_data):
    load_matrix = Hist_data[Hist_data.columns[3]].to_numpy() #takes the first column of data (tickers) and puts it in its own matrix
    close_data = load_matrix.tolist() # function allows for quick access to the closing prices from the excel file
    return close_data

def watchlist_reader():
    tic = time.perf_counter()
    watchlist_data = pd.read_csv("C:\\Users\\jared\\AutoTrader\\"+listex+".csv", skiprows=3) #reads the csv file exported from TOS
    matrix = watchlist_data[watchlist_data.columns[0]].to_numpy() #takes the first column of data (tickers) and puts it in its own matrix
    tickers = matrix.tolist() #converts matrix to a list ready for the remainder of code
    #very similar to the function list_len(), but this is used for grabbing data for calculations
    global j
    global close_prices
    global period
    j = 0
    global low_sma
    low_sma = []
    global low_rsi
    low_rsi = []
    global good_rsi
    good_rsi = []
    global time_up
    time_up = [] #sets global variables so that other functions can access what is put into the lists
    print('You are about to look at '+ str(len(tickers)) + ' companies historical data.')
    #shutil.rmtree("C:\\users\\jared\\documents\\STONKS\\Data\\")#deletes old files
    #os.mkdir("C:\\users\\jared\\documents\\STONKS\\Data\\")#makes new folder for new files
    #load_bar = tqdm(total = num_comps)
    # This while loop is reponsible for storing the historical data for each ticker in our list. Note that yahoo finance sometimes incurs json.decode errors and because of this we are sleeping for 2 seconds after each iteration, also if a call fails we are going to try to execute it again. Also, do not make more than 2,000 calls per hour or 48,000 calls per day or Yahoo Finance may block your IP. The clause "(Amount_of_API_Calls < 1800)" below will stop the loop from making too many calls to the yfinance API.Prepare for this loop to take some time. It is pausing for 2 seconds after importing each stock.
    # Used to iterate through our list of tickers
    bad_grabs = 0
    i=0
    while (i < 1): #loops through every ticker in the list that was selected
        low_rsi=[]
        low_sma=[]
        good_rsi=[]
        time_up=[]
        global previous_stocks
        previous_stocks = []
        try:
            stock = tickers[i]  # Gets the current stock ticker
            print(stock)
            current = r.stocks.get_stock_historicals(stock,interval='day',span='year',bounds='regular',info = None)
            close_prices = []
            b = 0
            while b < len(current):
                close_prices.append(float(current[b]['close_price']))
                b+=1
            period = 20 # Set period length used in the calculations
            print(len(close_prices))
            #len(close_prices)-period
            while j < len(close_prices)-period:     
                #print("Day "+str(j))
                param_dict = json.load(open('C:\\Users\\jared\\AutoTrader\\parameters.json'))
                portfolio = param_dict[0]['primary']['portfolio']
                port = json.load(open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json'))
                print(j)
                mov_avg = moving_avg_calc(close_prices,period) #puts the sma into a variable
                rsi_val = rsi_calc(stock,close_prices,period)#puts the rsi into a variable
                rsi_prev = rsi_calc_prev(stock,close_prices,period)
                rsi_compare(stock,rsi_val,rsi_prev)
                time_compare(stock,close_prices) #checks whether or not the stock is up on the timeline or not
                compare_sma_to_price(stock,close_prices,mov_avg,period)
                information() # calls the function to start the parameter calculations
                #reset()
                numbers_update()
                reset()
                j+=1
            bad_grabs = 0
            i += 1  # Iteration to the next ticker
        except TypeError:
            print("Error fetching data for "+str(stock)+"...")
            i+=1
        except ValueError:
            print("Error fetching data for "+str(stock)+"...")
            if bad_grabs > 3:
                i+=1
            bad_grabs+=1
        time.sleep(0.05)
        toc = time.perf_counter()
        print("\nAll data loaded and calculated in " + str(round(toc-tic,2)) + " seconds.")
        j=0
        #information() # calls the function to start the parameter calculations
        #decisions()
    

def moving_avg_calc(close_data, period):
    close_sum = 0
    if len(close_data)<period: # if there is not enough data to match the length of the period the SMA will not be calculated
        print("bad")
        return "NULL"
    for p in range(0,period):
        close_sum+=int(close_data[p+j]) 
        #print("i: "+str(i))
        #print("j: "+str(j))
    sma = close_sum/period # sums the closing prices for the length of the period then divides by the period to attain the SMA
    #print("SMA: "+str(sma))
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
        q = i+j+5
        if q <= len(close_data)-1:
            holding_price = float(close_data[i+j])
            new_price = float(close_data[i+1+j])
            holding_price = round(holding_price,2)
            new_price = round(new_price,2)
            #print(holding_price)
            #print(new_price)
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
        fax=""
        #print("Tried to divide by zero...")
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
        q = i+j+5
        if q <= len(close_data)-1:
            holding_price = float(close_data[i+5+j])
            new_price = float(close_data[i+4+j])
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
        fax = ""
        #print("Tried to divide by zero...")
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
        init_price = float(close_data[0+j])
        last_price = float(close_data[len(close_data)-1])
        
    except IndexError:
        print("Index Error")
        last_price = float(close_data[len(close_data)-1])
    
    change = float((last_price-init_price)/init_price*100)
    if change >= 10.0: #compares first and last closing data
        time_up.append(stock)   #adds current stock to a year-up list, if not then it does nothing

def information():    
    for i in low_rsi:
        if i in low_sma:
            if i in time_up:
                if i in good_rsi:#commented out for now bc theres not enough data
                    if i in previous_stocks:
                        continue
                    previous_stocks.append(i)
                    print(i+" is a buy")
    data = json.load(open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json'))
    data[0]['INFO']['stocks'] = previous_stocks
    with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
        json.dump(data,outfile, indent = 4)
    decisions()

#######################################################################################
    
def decisions():
    port = json.load(open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json'))
    cash = port[0]['INFO']['Cash']
    new_cash = cash
    #print("Cash: "+str(cash))
# =============================================================================
#     print ("The dictionary before performing remove is : " + str(port)) 
#     keep = port[0]
#     port.clear() 
#     port = keep
#     port['INFO']['stocks'] = stocks
#     print ("The dictionary after remove is : " + str(port))
#     if type(port) is dict:
#         port = [port]
#     with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
#         json.dump(port,outfile, indent = 4) 
# =============================================================================
    useable_cash = 0.80*cash
    i = 0
    while (i < len(stocks)):
        stock = stocks[i]
        print(stock)
        try:
            if port[i+1][stock]['status'] == "open" or port[i+1][stock]['status'] == "closed":
                i+=1
                continue
        except IndexError:
            print("Index Error")
            #del port[0]['INFO'][stocks][i]
            pass
        except KeyError:
            print("Key Error")
            del port[0]['INFO'][stocks][i]
        last_price = close_prices[j]
        #today = date.today()
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
                "date in" : j,
                "date out" : "null",
                "shares" : num_shares,
                "value" : round(num_shares*last_price,3),
                "override": "null"
                }}
        #print("---Upload dictionary---")
        #print(upload_dict)
        print(stock+" bought at "+str(last_price))
        port[0]['INFO']['Cash'] = new_cash
        port.append(upload_dict)
        with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
            json.dump(port,outfile, indent = 4)
        i+=1

#################################################################################
        
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
        print(port)
        print(j)
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
        #p_value += original_value
        #print("     Entry value for "+str(stock)+": "+str(round(original_value,2)))
        if close_prices == []:
            print("Cannot update this stock value right now.")
            i+=1
            continue
        last_price = close_prices[j]
        new_value = shares*last_price
        p_value+=new_value
        #print("     Current value for "+str(stock)+": "+str(round(new_value,2)))
        #print("Shares owned: "+str(shares))
        port[int(i)][stock]['value'] = new_value
        hold = round(new_value,2)-round(original_value,2)
        p_l += hold
        port[int(i)][stock]['p/l'] = hold
        i+=1
    #p_value += p_l
    p_value += cash
    p_value = round(p_value,2)
    cash = round(cash,2)
    #print("Cash: "+str(cash))
    #print("Portfolio Value: "+str(round(p_value,2)))
    port[0]['INFO']['Portfolio Value'] = p_value
    with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
        json.dump(port,outfile, indent = 4)
    #print("Realized Gain/loss: $"+str(round(p_l,2)))
    check_sell()

#################################################################################################

def check_sell():
    port = json.load(open(r"C:\\Users\\jared\\AutoTrader\\"+portfolio+".json"))
    cash = port[0]['INFO']['Cash']
    stonks = port[0]['INFO']['stocks']
    i=1
    p_l = 0
    p_value = 0
    while i <= len(stonks):
        #print(i)
        stock = stonks[i-1]
        shares = port[int(i)][stock]['shares']
        original_value = port[int(i)][stock]['enter price']*shares
        #p_value += old_value
        original_value = round(original_value,2)
        if port[int(i)][stock]['status'] == "closed":
            i+=1
            continue
        if close_prices == []:
            print("Cannot update this stock value right now.")
            i+=1
            continue
        last_price = close_prices[j]
        new_value = round(shares*last_price,2)
        p_value+=new_value
        if original_value == 0.0:
            print("Cannot execute...No shares owned")
            p_change = 0.0
        else:
            p_change = (new_value-original_value)/original_value
        if p_change < -0.03:
            #print("Limiting Losses...")
            port[int(i)][stock]['status'] = "to close"
        if p_change >= 0:
            if p_change >=0.015:
                #print(str(stock)+" is a SELL")
                #print("p/l "+ str(p_l))
                port[int(i)][stock]['status'] = "to close"
                #need to mark this stock for sale so that the next function can find it    
        else:
            u=0
            #print("Not enough movement...")
        hold = round(new_value,2)-round(original_value,2)
        p_l += hold
        i+=1
    #p_value += p_l
    p_value += cash
    cash = round(cash,2)
    #print("Portfolio Value: "+str(round(p_value,2)))
    port[0]['INFO']['Portfolio Value'] = round(p_value,2)
    with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
        json.dump(port,outfile, indent = 4)
    #print("Realized Gain/loss: $"+str(round(p_l,2)))
    sell_conf()    

def sell_conf():
    port = json.load(open(r"C:\\Users\\jared\\AutoTrader\\"+portfolio+".json"))
    #loop through the stock keys and find the ones that are marked for sale, then deactivate them but dont remove from file
    cash = port[0]['INFO']['Cash']
    stonks = port[0]['INFO']['stocks']
    #today = date.today()
    i=1
    while i <= len(stonks):
        stock = stonks[i-1]
        if port[int(i)][stock]['status'] == "to close" or port[int(i)][stock]['override']=="sell":
            last_price = close_prices[j]
            port[int(i)][stock]['exit price'] = round(last_price,2)
            cash+= port[int(i)][stock]['value']
            port[int(i)][stock]['date out'] = j
            pl = round(last_price-port[int(i)][stock]['enter price'],2)
            port[int(i)][stock]['p/l'] = pl
            port[int(i)][stock]['status'] = "closed"
            #playsound('cash_register.mp3')
            #print("exit price: "+str(last_price))
            #print("p/l "+str(pl))
            
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
            last_price = close_prices[j]
            port[int(i)][stock]['exit price'] = round(last_price,2)
            cash+= port[int(i)][stock]['value']
            port[int(i)][stock]['date out'] = j
            pl = round(last_price-port[int(i)][stock]['enter price'],2)
            port[int(i)][stock]['p/l'] = pl
            port[int(i)][stock]['status'] = "closed"
            #playsound('cash_register.mp3')
            #print("exit price: "+str(last_price))
            #print("p/l "+str(pl))
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
#################################################################################################
params()
watchlist_reader()