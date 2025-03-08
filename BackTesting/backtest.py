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

    def runAllBacktest():
        cerebro = bt.Cerebro()
        # Feed data into Backtrader
        btData15m = bt.feeds.PandasData(dataname=dl.Data(symbol='EURUSD').full_data)
        cerebro.adddata(btData15m)

        # Add a FixedSize sizer according to the stake
        cerebro.addsizer(bt.sizers.FixedSize, stake=10000)

        # Add a strategy optimization
        cerebro.optstrategy(
            MaCrossOverBt,
            maperiod=range(10, 15),
        )

        cerebro.optstrategy(
            MeanReversionStrategy,
            bollinger_period=range(10, 12),
        )

        cerebro.optstrategy(
            CrashBoomStrategy,
            bollinger_period=range(20, 31, 5),  # Steps of 2 (20, 22, 24)
            # ema_trend_period=range(50, 100, 10),  # Steps of 10 (50, 60, 70, 80, 90)
            # ema_signal_period=range(10,21,5),  # Steps of 5 (10, 15)
            # atr_period=range(7, 21, 7),  # Steps of 2 (7, 9, 11, 13)
        #     atr_mult=[1.0, 1.5, 2.0],  # Specific values
        #     profit_mult=[1, 1.5, 2],  # Specific values
        #     trail_trigger=range(10, 20, 5),  # Steps of 5 (10, 15)
        #     trail_atr_mult=[1, 1.5, 2],  # Specific values
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

        # Dictionary to store separate DataFrames for each strategy
        strategy_dfs = {}

        for run in results:
            for strategy in run:
                sharpe = strategy.analyzers.sharpe.get_analysis()
                drawdown = strategy.analyzers.drawdown.get_analysis()
                sqn = strategy.analyzers.sqn.get_analysis()
                params = strategy.params

                # Convert the params to a dict
                params_dict = dict(params._getkwargs()) if hasattr(params, '_getkwargs') else vars(params)

                # Create a combined dictionary with metrics and parameters
                combined = {
                    "sharpe_ratio": sharpe.get('sharperatio', float('nan')),
                    "max_drawdown": drawdown.max.drawdown if drawdown else float('nan'),
                    "sqn": sqn.get('sqn', float('nan')),
                }

                # Add strategy parameters to the dictionary, excluding 'name' to avoid redundancy
                strategy_name = params_dict.get('name', 'Unnamed Strategy')
                combined.update(params_dict)
                combined.pop('name', None)  # Remove the redundant 'name' parameter

                # If this strategy doesn't have a DataFrame yet, create it
                if strategy_name not in strategy_dfs:
                    strategy_dfs[strategy_name] = pd.DataFrame(columns=combined.keys())

                # Convert the combined dictionary to a DataFrame
                new_df = pd.DataFrame([combined])

                # Concatenate the new row with the existing DataFrame for the strategy
                strategy_dfs[strategy_name] = pd.concat([strategy_dfs[strategy_name], new_df], ignore_index=True)

        # Now each strategy will have its own DataFrame in the dictionary
        # Optionally, print each strategy's DataFrame for inspection
        for strategy_name, df in strategy_dfs.items():
            print(f"Strategy: {strategy_name}")
            print(df)
            print()

        return strategy_dfs  # Return the dictionary of DataFrames for further processing



                    
        

if __name__ == '__main__':
    # Required for Windows to properly handle multiprocessing
    multiprocessing.freeze_support()  

    Backtester.runAllBacktest()

    # Run the backtest using TestStrategy
    # Backtester.runBackTestForStrategy(CrashBoomStrategy, plot=True)
