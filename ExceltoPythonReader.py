# -*- coding: utf-8 -*-
"""
Created on Sun Sep  5 13:27:38 2021

@author: jared
"""
import pandas as pd

prices = pd.read_excel('result.xlsx',sheet_name=0,header=0,index_col=False)
show = prices.head()
#print(show)
print(prices[0])
FSR_data = prices["FSR"]
print(FSR_data[0])