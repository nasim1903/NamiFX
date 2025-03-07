import backtrader as bt
import backtrader.analyzers as btanalyzers
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

        # Add a FixedSize sizer according to the stake
        cerebro.addsizer(bt.sizers.FixedSize, stake=10000)

        # Add a strategy optimization
        cerebro.optstrategy(
            MaCrossOverBt,
            maperiod=range(10, 20),
        )

        cerebro.optstrategy(
            MeanReversionStrategy,
            bollinger_period=range(10, 15),
            atr_period=range(10, 13),
            atr_mult=range(2, 5),
            profit_mult=range(1, 3)
        )

        # Set initial cash
        cerebro.broker.setcash(100000)
        cerebro.broker.setcommission(0.01)

        # Add analyzers for performance metrics
        cerebro.addanalyzer(btanalyzers.SharpeRatio, _name="sharpe")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

        # Run optimization with multiprocessing
        results = cerebro.run(maxcpus=12)

        # List to store results for strategy ranking
        strategy_results = []

        # Loop through each set of results (for each optimized strategy)
        for run in results:
            for strategy in run:
                sharpe = strategy.analyzers.sharpe.get_analysis()
                drawdown = strategy.analyzers.drawdown.get_analysis()
                sqn = strategy.analyzers.sqn.get_analysis()

                # Collect performance metrics
                strategy_results.append({
                    "sharpe_ratio": sharpe.get('sharperatio', float('nan')),
                    "max_drawdown": drawdown.max.drawdown if drawdown else float('nan'),
                    "sqn": sqn.get('sqn', float('nan')),
                })

        # Convert to DataFrame for easier analysis and sorting
        df = pd.DataFrame(strategy_results)

        # Rank strategies based on Sharpe Ratio, Drawdown, and SQN (can adjust rankings as needed)
        df['rank'] = df['sharpe_ratio'] - df['max_drawdown'] + df['sqn']  # Example formula for ranking
        df = df.sort_values(by='rank', ascending=False)

        print("Strategy Ranking:")
        print(df)

        # Optionally, return the ranked strategies for further processing
        return df
            
        

if __name__ == '__main__':
    # Required for Windows to properly handle multiprocessing
    multiprocessing.freeze_support()  

    Backtester.runAllBacktest()

    # Run the backtest using TestStrategy
    # Backtester.runBackTestForStrategy(CrashBoomStrategy, plot=True)
