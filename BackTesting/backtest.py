import backtrader as bt
import sys
import os
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data import dataLoader as dl



class Backtester:
    @staticmethod
    def runBackTest():
        cerebro = bt.Cerebro()

        fxdata = dl.Data()

        twoWeekData = fxdata.get_last_2_weeks_data()

        # Ensure data is not empty
        if twoWeekData.empty :
            raise ValueError("Error: Loaded data is empty. Check the data source.")

        # Feed data into Backtrader
        btData = bt.feeds.PandasData(dataname=twoWeekData)
        cerebro.adddata(data=btData)

        # Set initial cash
        cerebro.broker.setcash(100000)
        print(f"Initial Broker Cash: {cerebro.broker.get_value()}")

        # Run backtest
        cerebro.run()

        # Plot results
        cerebro.plot(style='bar')


# Run the backtest
Backtester.runBackTest()
