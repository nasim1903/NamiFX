import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta

class Data: 

    def __init__(self, filename="market_data.csv"):
        self.filename = filename
        self.full_data = self._load_data()

    def _load_data(self):
        """Load market data from CSV."""
        try:
            df = pd.read_csv(self.filename, parse_dates=["time"])
            return df
        except FileNotFoundError:
            print("Market data file not found!")
            return pd.DataFrame()

    def get_last_2_weeks_data(self):
        """Retrieve the last 2 weeks of market data."""
        cutoff_date = datetime.now() - timedelta(weeks=2)
        return self.full_data[self.full_data["time"] >= cutoff_date]

    def get_live_data(self, symbol="EURUSD", timeframe=mt5.TIMEFRAME_M1, count=500):
        """Fetch latest market data from MT5."""
        if not mt5.initialize():
            print("MT5 Initialization failed!")
            return pd.DataFrame()

        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        mt5.shutdown()

        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df
