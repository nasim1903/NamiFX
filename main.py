import MetaTrader5 as mt5
import time
from BackTesting import backtest


def initialize_mt5():
    if not mt5.initialize():
        print("Initialize() failed, error code =", mt5.last_error())
        quit()
    else:
        print("MT5 initialized successfully")

initialize_mt5()

user_input = input("Press 1 to run the backtester: ")

if user_input == "1":
    backtester = backtest.Backtester()
    backtester.runBackTestForStrategy(plot=True)  
    print("Backtester has finished running.")
else:
    print("Invalid input. Exiting...")

while True:
    # Function for live trading will go here when ready
    time.sleep(1)
