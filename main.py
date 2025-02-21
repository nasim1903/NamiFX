import MetaTrader5 as mt5
import time

def initialize_mt5():
    if not mt5.initialize():
        print("Initialize() failed, error code =", mt5.last_error())
        quit()
    else:
        print("MT5 initialized successfully")

initialize_mt5()

while True:
    # Function for live trading will go here when ready
    time.sleep(1)
