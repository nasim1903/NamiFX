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
    def runBackTestForStrategy(strategy: Type[bt.Strategy], plot: bool = True, fxdata: dl.Data = dl.Data(timeframe=mt5.TIMEFRAME_H1, numOfCandles=1000, symbol='EURUSD')):
        """
        Runs a backtest using the provided strategy.

        :param strategy: The strategy class to be used for backtesting (must be a subclass of bt.Strategy).
        :param plot: Boolean to determine whether to plot the results. Will only run 1 instance of the strategy
        """
        cerebro = bt.Cerebro()

        # Feed data into Backtrader
        btData = bt.feeds.PandasData(dataname=fxdata.full_data)
        cerebro.adddata(btData)

        # Add a FixedSize sizer according to the stake
        cerebro.addsizer(bt.sizers.FixedSize, stake=10000)
        
        cerebro.addstrategy(strategy)

        # Set initial cash
        cerebro.broker.setcash(100000)
        cerebro.broker.setcommission(0.01)

        # Run optimization with multiprocessing
        cerebro.run()

        # Plot results if needed
        if plot:
            cerebro.plot(style='bar')

    def runAllBacktest():

        cerebro = bt.Cerebro()
        # Feed data into Backtrader
        
        btData15m = bt.feeds.PandasData(dataname=dl.Data(timeframe=mt5.TIMEFRAME_M15, symbol='EURUSD').get_last_2_weeks_data())
        btData1h = bt.feeds.PandasData(dataname=dl.Data(timeframe=mt5.TIMEFRAME_H1, symbol='EURUSD').get_last_2_weeks_data())
        
        cerebro.adddata(btData15m)
        cerebro.adddata(btData1h)

        # Add a FixedSize sizer according to the stake
        cerebro.addsizer(bt.sizers.FixedSize, stake=10000)

        cerebro.optstrategy(
            MaCrossOverBt,
            maperiod=range(10, 13),
            )

        # # Add a strategy
        cerebro.optstrategy(
            MeanReversionStrategy,
            bollinger_period=range(10, 11),
            atr_period = range(10,11),
            atr_mult=range(2,3),
            profit_mult=range(1,2)
            )

        # Set initial cash
        cerebro.broker.setcash(100000)

        cerebro.broker.setcommission(0.01)

        # Run optimization with multiprocessing
        cerebro.run()
        
        # # Flatten the results list
        # results = [strategy for sublist in results for strategy in sublist]

        # # Find the best-performing strategy
        # best_strategy = max(results, key=lambda strat: strat.broker.get_value())

        # # Print the best parameter
        # print(f"Best MA Period: {best_strategy.params.maperiod} with Final Value: {best_strategy.broker.get_value():.2f}")
    

if __name__ == '__main__':
    # Required for Windows to properly handle multiprocessing
    multiprocessing.freeze_support()  

    Backtester.runAllBacktest()

    # Run the backtest using TestStrategy
    # Backtester.runBackTestForStrategy(CrashBoomStrategy, plot=True)
