import pandas as pd
import MetaTrader5 as mt5
from datetime import datetime, timedelta

def get_last_2_weeks_data():
    """Load last 2 weeks of data from CSV"""
    try:
        df = pd.read_csv("market_data.csv", parse_dates=["time"])
        cutoff_date = datetime.now() - timedelta(weeks=2)
        return df[df["time"] >= cutoff_date]
    except FileNotFoundError:
        print("Market data file not found!")
        return pd.DataFrame()

def get_live_data(symbol="EURUSD", timeframe=mt5.TIMEFRAME_M1, count=500):
    """Fetch latest market data from MT5"""
    if not mt5.initialize():
        print("MT5 Initialization failed!")
        return pd.DataFrame()
    
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, count)
    mt5.shutdown()
    
    if rates is None:
        print("Failed to retrieve data from MT5.")
        return pd.DataFrame()

    df = pd.DataFrame(rates)
    df["time"] = pd.to_datetime(df["time"], unit="s")
    return df

# # Usage
# from dataLoader import get_last_2_weeks_data, get_live_data

# historical_data = get_last_2_weeks_data()
# live_data = get_live_data("GBPUSD")
