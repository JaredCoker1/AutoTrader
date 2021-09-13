# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 11:17:22 2021

@author: jared
"""
import json
import Stock_Scanner as ss
import yfinance as yf
from datetime import date
from playsound import playsound
import RobinExec

def params():
    global stocks
    global portfolio
    param_dict = json.load(open('C:\\Users\\jared\\AutoTrader\\parameters.json'))
    portfolio = param_dict[0]['primary']['portfolio']
    port = json.load(open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json'))
    stocks = port[0]['INFO']['stocks']

def check_sell():
    port = json.load(open(r"C:\\Users\\jared\\AutoTrader\\"+portfolio+".json"))
    cash = port[0]['INFO']['Cash']
    stonks = port[0]['INFO']['stocks']
    i=1
    p_l = 0
    p_value = 0
    while i <= len(stonks):
        print(i)
        stock = stonks[i-1]
        shares = port[int(i)][stock]['shares']
        original_value = port[int(i)][stock]['enter price']*shares
        #p_value += old_value
        original_value = round(original_value,2)
        temp = yf.Ticker(str(stock))
        Hist_data = temp.history(period="1m")
        close_prices = ss.close_grab(Hist_data)
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
            print("Limiting Losses...")
            port[int(i)][stock]['status'] = "to close"
        if p_change >= 0:
            if p_change >=0.015:
                print(str(stock)+" is a recommended SELL")
                port[int(i)][stock]['status'] = "to close"
                #need to mark this stock for sale so that the next function can find it    
        else:
            print("Not enough movement...")
        hold = round(new_value,2)-round(original_value,2)
        p_l += hold
        i+=1
    #p_value += p_l
    p_value += cash
    cash = round(cash,2)
    print("Portfolio Value: "+str(round(p_value,2)))
    port[0]['INFO']['Portfolio Value'] = round(p_value,2)
    with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
        json.dump(port,outfile, indent = 4)
    print("Realized Gain/loss: $"+str(round(p_l,2)))
    sell_conf()

def sell_conf():
    port = json.load(open(r"C:\\Users\\jared\\AutoTrader\\"+portfolio+".json"))
    #loop through the stock keys and find the ones that are marked for sale, then deactivate them but dont remove from file
    cash = port[0]['INFO']['Cash']
    stonks = port[0]['INFO']['stocks']
    today = date.today()
    i=1
    while i <= len(stonks):
        stock = stonks[i-1]
        if port[int(i)][stock]['status'] == "to close":
            temp = yf.Ticker(str(stock))
            Hist_data = temp.history(period="1m")
            close_prices = ss.close_grab(Hist_data)
            last_price = close_prices[len(close_prices)-1]
            port[int(i)][stock]['exit price'] = round(last_price,2)
            cash+= port[int(i)][stock]['value']
            port[int(i)][stock]['date out'] = str(today.strftime("%m/%d/%y"))
            pl = round(last_price-port[int(i)][stock]['enter price'],2)
            port[int(i)][stock]['p/l'] = pl
            RobinExec.params()
            RobinExec.login()
            RobinExec.Robin_Sell()
            #playsound('cash_register.mp3')
        i+=1   
    port[0]['INFO']['Cash'] = round(cash,2)
    with open('C:\\Users\\jared\\AutoTrader\\'+portfolio+'.json', 'w') as outfile:
        json.dump(port,outfile, indent = 4)