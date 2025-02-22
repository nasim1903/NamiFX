import backtrader as bt
import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data import dataLoader as dl

# Create a Stratey
class TestStrategy(bt.Strategy):

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        if self.dataclose[0] < self.dataclose[-1]:
            # current close less than previous close
            if self.dataclose[-1] < self.dataclose[-2]:
                # previous close less than the previous close

                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.buy()


class Backtester:

    @staticmethod

    def runBackTestForStrategy(plot=False):
        cerebro = bt.Cerebro()

        fxdata = dl.Data()

        twoWeekData = fxdata.get_last_2_weeks_data()

        # Ensure data is not empty
        if twoWeekData.empty :
            raise ValueError("Error: Loaded data is empty. Check the data source.")

        # Feed data into Backtrader
        btData = bt.feeds.PandasData(dataname=twoWeekData)
        cerebro.adddata(data=btData)
        cerebro.addstrategy(TestStrategy)
        # Set initial cash
        cerebro.broker.setcash(100000)
        print(f"Initial Broker Cash: {cerebro.broker.get_value()}")

        # Run backtest
        cerebro.run()

        if plot == True:
            cerebro.plot(style='bar')

        print(f"Final Broker Cash: {cerebro.broker.get_value()}")

        # Plot results


# Run the backtest
# Backtester.runBackTestForStrategy()
