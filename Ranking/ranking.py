import sys
import os
import pandas as pd
import MetaTrader5 as mt5
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from BackTesting import backtest

# Create an instance of BackTester

def convertDfToCsv(df, filename="backtest_results.csv"):
    """
    Saves the given DataFrame as a CSV file in the current directory.

    :param df: The DataFrame to save.
    :param filename: Optional filename for the CSV (default: "backtest_results.csv").
    """
    if df is not None and not df.empty:
        file_path = os.path.join(os.getcwd(), filename)
        df.to_csv(file_path, index=False)
        print(f"CSV file saved successfully at: {file_path}")
    else:
        print("No data to save.")


# Run the function correctly
df = backtest.Backtester.runAllBackTests()
convertDfToCsv(df)
