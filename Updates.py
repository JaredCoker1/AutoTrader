# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 15:36:10 2021

@author: jared
"""
import json
import yfinance as yf
import Stock_Scanner as ss
import robin_stocks.robinhood as r

def params():
    global stocks
    global portfolio
    global port
    param_dict = json.load(open('C:\\Users\\jared\\AutoTrader\\parameters.json'))
    portfolio = param_dict[0]['primary']['portfolio']
    port = json.load(open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json'))
    stocks = port[0]['INFO']['stocks']

def login():
    login = r.login('**************','*******')
    my_account = r.profiles.load_account_profile(info=None)
    port[0]['INFO']['Cash'] = float(my_account['buying_power'])
    with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
        json.dump(port,outfile, indent = 4)

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
        #p_value += original_value
        print("     Entry value for "+str(stock)+": "+str(round(original_value,2)))
        temp = yf.Ticker(str(stock))
        Hist_data = temp.history(period="1m")
        close_prices = ss.close_grab(Hist_data)
        if close_prices == []:
            print("Cannot update this stock value right now.")
            i+=1
            continue
        last_price = close_prices[len(close_prices)-1]
        new_value = shares*last_price
        p_value+=new_value
        print("     Current value for "+str(stock)+": "+str(round(new_value,2)))
        print("Shares owned: "+str(shares))
        port[int(i)][stock]['value'] = new_value
        hold = round(new_value,2)-round(original_value,2)
        p_l += hold
        port[int(i)][stock]['p/l'] = hold
        i+=1
    #p_value += p_l
    p_value += cash
    p_value = round(p_value,2)
    cash = round(cash,2)
    print("Cash: "+str(cash))
    print("Portfolio Value: "+str(round(p_value,2)))
    port[0]['INFO']['Portfolio Value'] = p_value
    with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
        json.dump(port,outfile, indent = 4)
    print("Realized Gain/loss: $"+str(round(p_l,2)))