import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta

mt5.initialize()

class Data:
    """
    A class to handle market data retrieval from MetaTrader 5.
    """

    def __init__(self, numOfCandles=28800, symbol='EURUSD', timeframe=mt5.TIMEFRAME_M15):
        self.numOfCandles = numOfCandles
        self.symbol = symbol
        self.timeframe = timeframe
        self.full_data = self.load_data()

    def load_data(self):
        """
        Load market data from MetaTrader 5.
        """
        rates = mt5.copy_rates_from_pos(self.symbol, self.timeframe, 0, self.numOfCandles)
        if rates is None:
            print("Failed to get market data from MT5")
            return pd.DataFrame()
        else:
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            df.set_index('time', inplace=True) 
            # Ensure column names match Backtrader's expectations
            df = df.rename(columns={'tick_volume': 'volume'})
            return df

    def get_last_2_weeks_data(self):
        """
        Retrieve the last 2 weeks of market data.
        """
        cutoff_date = datetime.now() - timedelta(weeks=2)
        return self.full_data[self.full_data.index >= cutoff_date]  # Compare with index
    
    def get_last_month_data(self):
        """
        Retrieve the last 2 weeks of market data.
        """
        cutoff_date = datetime.now() - timedelta(weeks=4)
        return self.full_data[self.full_data.index >= cutoff_date]  # Compare with index

    def get_live_data(self, symbol="EURUSD", timeframe=mt5.TIMEFRAME_M1, count=500):
        """
        Fetch latest market data from MetaTrader 5.
        """
        if not mt5.initialize():
            print("MT5 Initialization failed!")
            return pd.DataFrame()

        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)

        df = pd.DataFrame(rates)
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df.set_index('time', inplace=True) 
        # Ensure column names match Backtrader's expectations
        df = df.rename(columns={'tick_volume': 'volume'})
        return df
