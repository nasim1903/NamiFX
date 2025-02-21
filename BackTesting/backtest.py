import backtrader as bt
import sys
import os
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data import dataLoader as dt


class Backtester:
    @staticmethod
    def runBackTest():
        cerebro = bt.Cerebro()

        fxdata = dt.Data()._load_data()

        # Ensure data is not empty
        if fxdata.empty:
            raise ValueError("Error: Loaded data is empty. Check the data source.")

        # Remove NaN and Inf values
        fxdata.dropna(inplace=True)
        fxdata = fxdata[~fxdata.isin([float('inf'), float('-inf')]).any(axis=1)]

        # Print debug info
        print(f"Data Shape: {fxdata.shape}")
        print(fxdata.head())

        # Feed data into Backtrader
        btData = bt.feeds.PandasData(dataname=fxdata)
        cerebro.adddata(data=btData)

        # Set initial cash
        cerebro.broker.setcash(100000)
        print(f"Initial Broker Cash: {cerebro.broker.get_value()}")

        # Run backtest
        cerebro.run()

        # Plot results
        cerebro.plot()


# Run the backtest
Backtester.runBackTest()
