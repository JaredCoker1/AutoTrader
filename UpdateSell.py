# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 11:22:09 2021

@author: jared
"""

import Updates as up
import Sell

up.params()
up.login()
up.numbers_update()

Sell.params()
Sell.check_sell()

