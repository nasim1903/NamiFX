import backtrader as bt
from Data import dataLoader as dt

class Backtester:

    def runBackTest():
        cerebro = bt.Cerebro()
        
        cerebro.broker.setcash(100000)
        print(cerebro.broker.get_value())

        cerebro.run()


Backtester.runBackTest()
