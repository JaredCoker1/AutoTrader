# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 13:27:39 2021

@author: jared
"""
import json
import yfinance as yf
from datetime import date
import Stock_Scanner as ss
import robin_stocks.robinhood as r
import RobinExec


def robinhood():
    login = r.login('*****************','************')

def params():
    global stocks
    global portfolio
    param_dict = json.load(open('C:\\Users\\jared\\AutoTrader\\parameters.json'))
    portfolio = param_dict[0]['primary']['portfolio']
    port = json.load(open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json'))
    stocks = port[0]['INFO']['stocks']

def decisions():
    port = json.load(open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json'))
    cash = port[0]['INFO']['Cash']
    new_cash = cash
    print("Cash: "+str(cash))
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
        try:
            if port[i+1][stock]['status'] == "to open" or port[i+1][stock]['status'] == "closed":
                i+=1
                continue
        except IndexError:
            pass
        temp = yf.Ticker(str(stock))
        Hist_data = temp.history(period="1y")
        close_prices = ss.close_grab(Hist_data)
        last_price = close_prices[len(close_prices)-1]
        today = date.today()
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
                "status" : "to open",
                "date in" : str(today.strftime("%m/%d/%y")),
                "date out" : "null",
                "shares" : num_shares,
                "value" : round(num_shares*last_price,3)
                }}
        print("---Upload dictionary---")
        print(upload_dict)
        port[0]['INFO']['Cash'] = new_cash
        port.append(upload_dict)
        with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
            json.dump(port,outfile, indent = 4)
        i+=1
    
    RobinExec.params()
    RobinExec.login()
    RobinExec.Robin_Buy()