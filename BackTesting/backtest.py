import backtrader as bt
import sys
import os
import pandas as pd
from typing import Type  # Import for type hinting

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data import dataLoader as dl
from Strategies.TestStrategy import TestStrategy 


class Backtester:

    @staticmethod
    def runBackTestForStrategy(strategy: Type[bt.Strategy], plot: bool = False):
        """
        Runs a backtest using the provided strategy.

        :param strategy: The strategy class to be used for backtesting (must be a subclass of bt.Strategy).
        :param plot: Boolean to determine whether to plot the results.
        """
        cerebro = bt.Cerebro()

        fxdata = dl.Data()
        twoWeekData = fxdata.get_last_2_weeks_data()

        # Ensure data is not empty
        if twoWeekData.empty:
            raise ValueError("Error: Loaded data is empty. Check the data source.")

        # Feed data into Backtrader
        btData = bt.feeds.PandasData(dataname=twoWeekData)
        cerebro.adddata(btData)

        # Add the provided strategy dynamically
        cerebro.addstrategy(strategy)

        # Set initial cash
        cerebro.broker.setcash(100000)
        cerebro.broker.setcommission(commission=0.001)
        print(f"Initial Broker Cash: {cerebro.broker.get_value()}")

        # Run backtest
        cerebro.run()

        # Plot results if needed
        if plot:
            cerebro.plot(style='bar')

        print(f"Final Broker Cash: {cerebro.broker.get_value()}")


# Run the backtest using TestStrategy
# Backtester.runBackTestForStrategy(TestStrategy, plot=True)
