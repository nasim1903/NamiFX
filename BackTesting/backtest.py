import backtrader as bt

class Backtester:

    def runBackTest():
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(100000)
        print(cerebro.broker.get_value())
        
        cerebro.run()


Backtester.runBackTest()
