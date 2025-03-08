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
    def runBackTestForStrategy(strategy: Type[bt.Strategy], plot: bool = True, fxdata: dl.Data = dl.Data(symbol='EURUSD')):
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
                # Add analyzers for performance metrics
        cerebro.addanalyzer(btanalyzers.SharpeRatio, _name="sharpe")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

        # Set initial cash
        cerebro.broker.setcash(100000)

        # Run optimization with multiprocessing
        result = cerebro.run()

        print(f"Sharpe: {result[0].analyzers.sharpe.get_analysis().get('sharperatio')}")

        # Plot results if needed
        if plot:
            cerebro.plot(style='bar')


    def runOptBacktest(strategy: Type[bt.Strategy], maxcpus: int = 12, fxdata: dl.Data = dl.Data(timeframe=mt5.TIMEFRAME_M1, symbol='EURUSD').get_last_month_data(), params = None):
        cerebro = bt.Cerebro(optreturn=False)  # Create a new Cerebro instance

        if params is None:
            params = {}  # Default to an empty dictionary if no params are provided

        cerebro.optstrategy(strategy, **params)  # Unpack params dictionary into optstrategy

        # Set initial cash
        cerebro.broker.setcash(10000)
        btData15m = bt.feeds.PandasData(dataname=fxdata)
        cerebro.adddata(btData15m)
        # Add a FixedSize sizer according to the stake
        cerebro.addsizer(bt.sizers.FixedSize, stake=1000)

        # Add analyzers for performance metrics
        cerebro.addanalyzer(btanalyzers.SharpeRatio, _name="sharpe")
        cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        cerebro.addanalyzer(bt.analyzers.SQN, _name="sqn")

        result = cerebro.run(maxcpus=maxcpus)  # Run backtest with specified CPU cores
        
        # Collecting results into a list of dictionaries
        results_data = []

        for run in result:
            for strategy in run:
                sharpe = strategy.analyzers.sharpe.get_analysis().get("sharperatio")
                drawdown = strategy.analyzers.drawdown.get_analysis().get("drawdown")
                sqn = strategy.analyzers.sqn.get_analysis().get("sqn")
                tradesTaken = strategy.analyzers.sqn.get_analysis().get("trades")
                params = strategy.params  # You can expand this if you want specific param info
                
                # Collect the data for each strategy run
                results_data.append({
                    'Sharpe Ratio': sharpe,
                    'Max Drawdown': drawdown,
                    'SQN': sqn,
                    'Trades Taken': tradesTaken,
                })

        # Create DataFrame from collected results
        df = pd.DataFrame(results_data)

        # Print or return the DataFrame
        print(df)
        return df


    def runAllBacktest():
        cerebro = bt.Cerebro()
        # Feed data into Backtrader
        btData15m = bt.feeds.PandasData(dataname=dl.Data(symbol='EURUSD').full_data)
        cerebro.adddata(btData15m)

        trendParams = {
            'ema_period': range(100, 201, 20),  # 20 to 200, step 10
            'atr_mult_sl': [1.5, 2, 2.5, 3],    # 1.5x to 3x for SL
            'atr_mult_tp': [2, 2.5, 3],         # 2x to 3x for TP (for a 1:2 to 1:3 risk-reward ratio)
        }

        crashStrategy = Backtester.runOptBacktest(TrendFollowingStrategy, maxcpus=12, fxdata = btData15m, params=trendParams)


        crashBoomParams = {
            "bollinger_period": range(20, 31, 5),  
            "ema_trend_period": range(50, 100, 10),
            "ema_signal_period": range(10, 21, 5), 
        }
        crashStrategy = Backtester.runOptBacktest(CrashBoomStrategy, maxcpus=12, fxdata = btData15m, params=crashBoomParams)


        maCrossOverParams = {
             "maperiod": range(10, 15, 2)
        }
        maCrossStrategy = Backtester.runOptBacktest(MaCrossOverBt, maxcpus=12, fxdata = btData15m, params=maCrossOverParams)
        
        
        meanReversionParams = {
            "bollinger_period": range(10, 13),
        }
        meanReversionStrat = Backtester.runOptBacktest(MeanReversionStrategy, maxcpus=12, fxdata = btData15m, params=meanReversionParams)

        print(f"Crash: \n{crashStrategy} \nCross:\n{maCrossStrategy}\nMean Reversion:\n{meanReversionStrat}")


                    
        

if __name__ == '__main__':
    # Required for Windows to properly handle multiprocessing
    multiprocessing.freeze_support()  

    trendParams = {
        'ema_period': range(100, 201, 20),  # 20 to 200, step 10
        'atr_mult_sl': [1.5, 2, 2.5, 3],    # 1.5x to 3x for SL
        'atr_mult_tp': [2, 2.5, 3],         # 2x to 3x for TP (for a 1:2 to 1:3 risk-reward ratio)
    }

    crashStrategy = Backtester.runOptBacktest(TrendFollowingStrategy, maxcpus=12, params=trendParams)

    # Run the backtest using TestStrategy
    # Backtester.runBackTestForStrategy(TrendFollowingStrategy, plot=True)
