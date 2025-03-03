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
from Strategies.MeanReversion import MeanReversionStrategy 
from Strategies.SupplyAndDemand import TrendFollowingStrategy
from Strategies.CrashAndBoom import CrashBoomStrategy



class Backtester:

    @staticmethod
    def runBackTestForStrategy(strategy: Type[bt.Strategy], plot: bool = False):
        """
        Runs a backtest using the provided strategy.

        :param strategy: The strategy class to be used for backtesting (must be a subclass of bt.Strategy).
        :param plot: Boolean to determine whether to plot the results.
        """
        cerebro = bt.Cerebro()

        fxdata = dl.Data(timeframe=mt5.TIMEFRAME_H1, numOfCandles=1000, symbol='GBPUSD')
        twoWeekData = fxdata.full_data

        # Ensure data is not empty
        if twoWeekData.empty:
            raise ValueError("Error: Loaded data is empty. Check the data source.")

        # Feed data into Backtrader
        btData = bt.feeds.PandasData(dataname=twoWeekData)
        cerebro.adddata(btData)

        # Add a FixedSize sizer according to the stake
        cerebro.addsizer(bt.sizers.FixedSize, stake=10000)
        

        # Add a strategy
        # strats = cerebro.optstrategy(
        #     strategy,
        #     bollinger_period=range(10, 20),
        #     atr_period = range(10,20),
        #     atr_mult=range(2,10),
        #     profit_mult=range(1,10)
        #     )

        cerebro.addstrategy(strategy)

        # Set initial cash
        cerebro.broker.setcash(100000)

        # Run optimization with multiprocessing
        results = cerebro.run(maxcpus=12)

        # # Flatten the results list
        # results = [strategy for sublist in results for strategy in sublist]

        # # Find the best-performing strategy
        # best_strategy = max(results, key=lambda strat: strat.broker.get_value())

        # # Print the best parameter
        # print(f"Best MA Period: {best_strategy.params.maperiod} with Final Value: {best_strategy.broker.get_value():.2f}")

        # Plot results if needed
        if plot:
            cerebro.plot(style='bar')




if __name__ == '__main__':
    # Required for Windows to properly handle multiprocessing
    multiprocessing.freeze_support()  
    # Run the backtest using TestStrategy
    Backtester.runBackTestForStrategy(CrashBoomStrategy, plot=True)
