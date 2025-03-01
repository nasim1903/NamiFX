import backtrader as bt
import sys
import os
import pandas as pd
import MetaTrader5 as mt5
from typing import Type  # Import for type hinting
import multiprocessing

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data import dataLoader as dl
from Strategies.MaCrossOver import MaCrossOverBt 


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
        twoWeekData = fxdata.full_data

        # Ensure data is not empty
        if twoWeekData.empty:
            raise ValueError("Error: Loaded data is empty. Check the data source.")

        # Feed data into Backtrader
        btData = bt.feeds.PandasData(dataname=twoWeekData)
        cerebro.adddata(btData)

        # Add a FixedSize sizer according to the stake
        cerebro.addsizer(bt.sizers.FixedSize, stake=1000)

        # Add a strategy
        # strats = cerebro.optstrategy(
        #     MaCrossOverBt,
        #     maperiod=range(5, 25))

        cerebro.addstrategy(MaCrossOverBt)

        # Set initial cash
        cerebro.broker.setcash(100000)
        cerebro.broker.setcommission(commission=0.01)
        print(f"Initial Broker Cash: {cerebro.broker.get_value()}")

        # Run backtest
        cerebro.run(maxcpus=12)

        # Plot results if needed
        if plot:
            cerebro.plot(style='bar')

        print(f"Final Broker Cash: {cerebro.broker.get_value()}")



if __name__ == '__main__':
    # Required for Windows to properly handle multiprocessing
    multiprocessing.freeze_support()  
    # Run the backtest using TestStrategy
    Backtester.runBackTestForStrategy(MaCrossOverBt, plot=True)
