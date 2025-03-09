import sys
import os
import pandas as pd
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



def readCsvToDf(filename="backtest_results.csv"):
    """
    Reads a CSV file and converts it into a Pandas DataFrame.

    :param filename: The name of the CSV file (default: "backtest_results.csv").
    :return: A Pandas DataFrame containing the CSV data.
    """
    file_path = os.path.join(os.getcwd(), filename)
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        print("CSV data loaded successfully:")
        print(df)
        return df
    else:
        print("Error: File not found.")
        return None


