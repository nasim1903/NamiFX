import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data import dataLoader as dl
import pandas as pd
import backtrader as bt
import MetaTrader5 as mt5


class MaCrossOverBt(bt.Strategy):

    print("hello")

class MacrossOverLive():

    def __init__(self, data, symbol='EURUSD', timeframe=mt5.TIMEFRAME_M15):
        self.symbol = symbol
        self.timeframe = timeframe

    


    