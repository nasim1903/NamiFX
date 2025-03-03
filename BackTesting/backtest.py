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
    def runBackTestForStrategy(strategy: Type[bt.Strategy], plot: bool = True, fxdata: dl.Data = dl.Data(timeframe=mt5.TIMEFRAME_M15, numOfCandles=1000, symbol='EURUSD')):
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
            

    def runAllBacktest(fxdata: dl.Data = dl.Data(timeframe=mt5.TIMEFRAME_M15, numOfCandles=1000, symbol='EURUSD')):

        cerebro = bt.Cerebro()
        # Feed data into Backtrader
        
        btData = bt.feeds.PandasData(dataname=fxdata.full_data)
        cerebro.adddata(btData)

        # Add a FixedSize sizer according to the stake
        cerebro.addsizer(bt.sizers.FixedSize, stake=10000)
        
        # Add a strategy
        cerebro.optstrategy(
            MeanReversionStrategy,
            bollinger_period=range(10, 20),
            atr_period = range(10,20),
            atr_mult=range(2,10),
            profit_mult=range(1,10)
            )

        cerebro.addstrategy(MeanReversionStrategy)

        # Set initial cash
        cerebro.broker.setcash(100000)

        cerebro.broker.setcommission(0.01)



        # Run optimization with multiprocessing
        cerebro.run(maxcpus=12)
        
        # # Flatten the results list
        # results = [strategy for sublist in results for strategy in sublist]

        # # Find the best-performing strategy
        # best_strategy = max(results, key=lambda strat: strat.broker.get_value())

        # # Print the best parameter
        # print(f"Best MA Period: {best_strategy.params.maperiod} with Final Value: {best_strategy.broker.get_value():.2f}")
    


if __name__ == '__main__':
    # Required for Windows to properly handle multiprocessing
    multiprocessing.freeze_support()  
    # Run the backtest using TestStrategy
    Backtester.runBackTestForStrategy(TrendFollowingStrategy, plot=True)
