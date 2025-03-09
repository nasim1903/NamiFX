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
        df = df.round(2)  # Round all numerical values to two decimal places
        print("CSV data loaded successfully:")
        print(df)
        return df
    else:
        print("Error: File not found.")
        return None

def rankStrategies(df):
    """
    Filters and ranks strategies based on performance metrics.
    
    :param df: The DataFrame containing strategy performance data.
    :param min_score: The minimum score required to allow trades.
    :return: A ranked DataFrame with the best strategies.
    """
    # Filter out strategies that did not trade
    df = df[df['Trades Taken'] > 0]
    
    # Filter out strategies with negative Sharpe Ratio
    df = df[df['Sharpe Ratio'] > 0]
    
    # Standardize key metrics using Z-score normalization
    df['Final Balance Z'] = (df['Final Balance'] - df['Final Balance'].mean()) / df['Final Balance'].std()
    df['Sharpe Ratio Z'] = (df['Sharpe Ratio'] - df['Sharpe Ratio'].mean()) / df['Sharpe Ratio'].std()
    df['SQN Z'] = (df['SQN'] - df['SQN'].mean()) / df['SQN'].std()
    df['Max Drawdown Adj'] = -df['Max Drawdown']  # Lower drawdown is better, so we negate it
    
    # Calculate weighted score
    df['Score'] = (
        0.40 * df['Final Balance Z'] +
        0.20 * df['Sharpe Ratio Z'] +
        0.10 * df['SQN Z'] +
        0.30 * df['Max Drawdown Adj']
    )
    
    # Round values to two decimal places
    df = df.round({'Score': 2, 'Final Balance Z': 2, 'Sharpe Ratio Z': 2, 'SQN Z': 2, 'Max Drawdown Adj': 2})
    
    # Sort by Score in descending order
    df = df.sort_values(by='Score', ascending=False)
    
    print(df[['Strategy', 'Symbol', 'Score']])
    return df

# Example usage
df = readCsvToDf()
if df is not None:
    ranked_df = rankStrategies(df)
