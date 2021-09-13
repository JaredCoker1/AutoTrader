# -*- coding: utf-8 -*-
"""
Created on Sat Apr 10 12:08:37 2021

@author: jared
"""

import json
import Stock_Scanner as ss
import yfinance as yf
from datetime import date
from playsound import playsound
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
    login = r.login('*****************','***********')
    my_account = r.profiles.load_account_profile(info=None)
    port[0]['INFO']['Cash'] = my_account['buying_power']
    
def Robin_Buy():
    i = 1
    while i <= len(stocks):
        stock = stocks[i-1]
        if port[i][stock]['status'] == "to open":
            print(stock+" is buy")
            val = r.get_quotes(stock,info=None)
            print("Yfinance price: "+str(port[i][stock]['enter price']))
            print("Robinhood price: "+str(val[0]['last_trade_price']))
            r.order_buy_market(stock,port[i][stock]['shares'])
            port[i][stock]['status'] = "open"
            with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
                json.dump(port,outfile, indent = 4)
        i+=1

def Robin_Sell():
    i = 1
    while i <= len(stocks):
        port = json.load(open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json'))
        stock = stocks[i-1]
        if port[i][stock]['status'] == "to close":
            print(stock+" is sell")
            val = r.get_quotes(stock,info=None)
            print("Yfinance price: "+str(port[i][stock]['enter price']))
            print("Robinhood price: "+str(val[0]['last_trade_price']))
            try:
                r.order_sell_market(stock,port[i][stock]['shares'])
                port[i][stock]['status'] = "closed"
                #playsound("cash_register.mp3")
                with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
                    json.dump(port,outfile, indent = 4)
            except:
                port[i][stock]['status'] = "closed"
            with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
                    json.dump(port,outfile, indent = 4)
        i+=1

def check():
    #must compare the json list and portfolio to what was actually bought on Robinhood
    #some companies are not supported, some transactions do not go through
    #the Robinhood portfolio and json portfolio need to be showing the same numbers
    return
