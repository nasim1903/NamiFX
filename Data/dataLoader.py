import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta

class MarketData:
    _instance = None  # Singleton instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketData, cls).__new__(cls)
            cls._instance.full_data = cls._load_data()
        return cls._instance

    @staticmethod
    def _load_data():
        """Load all historical data from CSV or MT5"""
        try:
            return pd.read_csv("market_data.csv", parse_dates=["time"])
        except FileNotFoundError:
            print("Market data file not found!")
            return pd.DataFrame()  # Return empty DataFrame if file is missing

    def get_last_2_weeks_data(self):
        """Return only the last 2 weeks of data"""
        if self.full_data.empty:
            return self.full_data
        cutoff_date = datetime.now() - timedelta(weeks=2)
        return self.full_data[self.full_data["time"] >= cutoff_date]

    def get_live_data(self, symbol="EURUSD", timeframe=mt5.TIMEFRAME_M1, count=500):
        """Fetch latest market data from MT5"""
        if not mt5.initialize():
            print("MT5 Initialization failed!")
            return pd.DataFrame()
        
        # Get latest 'count' bars
        rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
        mt5.shutdown()
        
        if rates is None:
            print("Failed to retrieve data from MT5.")
            return pd.DataFrame()
        
        # Convert to DataFrame
        df = pd.DataFrame(rates)
        df["time"] = pd.to_datetime(df["time"], unit="s")  # Convert timestamps
        
        return df

# # Usage Example
# if __name__ == "__main__":
#     market_data = MarketData()

#     # Get last 2 weeks of historical data
#     historical_data = market_data.get_last_2_weeks_data()
#     print(historical_data.tail())

#     # Get latest live data from MT5
#     live_data = market_data.get_live_data(symbol="GBPUSD", timeframe=mt5.TIMEFRAME_M5)
#     print(live_data.tail())
