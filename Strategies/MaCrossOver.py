import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data import dataLoader as dl
import pandas as pd
import backtrader as bt
import MetaTrader5 as mt5


class MaCrossOverBt(bt.Strategy):
    params = (
        ('maperiod', 34),
        ('maperiod2', 50),
        ('printlog', False),
        ('pip_value', 0.0001),  # Default pip value for most currency pairs
        ('stop_loss', 30),  # 10 pips stop loss
        ('take_profit', 100),  # 10 pips take profit
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy '''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.sma = bt.indicators.ExponentialMovingAverage(
            self.datas[0], period=self.params.maperiod)
        self.ema = bt.indicators.ExponentialMovingAverage(
            self.datas[0], period=self.params.maperiod2)
                # Initialize variable for tracking all-time high
        self.all_time_high = self.broker.get_cash()

    def stop(self):
        self.log(f'Final Value: {self.broker.get_cash():.2f}', doprint=True)
        self.log(f'ma: {self.params.maperiod}', doprint=True)


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.5f}')
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.5f}')
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def next(self):

        # Update all-time high
        current_value = self.broker.get_cash()
        if current_value > self.all_time_high:
            self.all_time_high = current_value


        if self.order:
            return

        if not self.position:
            if self.sma[0] > self.ema[0]:
                self.log(f'BUY CREATE, {self.dataclose[0]:.5f}')
                self.order = self.buy()

                # Define stop loss and take profit prices
                stop_loss_price = self.dataclose[0] - (self.params.stop_loss * self.params.pip_value)


                take_profit_price = self.dataclose[0] + (self.params.take_profit * self.params.pip_value)

                # Place stop loss order
                self.sell(exectype=bt.Order.Stop, price=stop_loss_price)
                # Place take profit order
                self.sell(exectype=bt.Order.Limit, price=take_profit_price)

        else:
            if self.sma[0] < self.ema[0]:
                self.log(f'SELL CREATE, {self.dataclose[0]:.5f}')
                self.order = self.sell()

                # Define stop loss and take profit prices
                stop_loss_price = self.dataclose[0] + (self.params.stop_loss * self.params.pip_value)
                take_profit_price = self.dataclose[0] - (self.params.take_profit * self.params.pip_value)

                # Place stop loss order
                self.buy(exectype=bt.Order.Stop, price=stop_loss_price)
                # Place take profit order
                self.buy(exectype=bt.Order.Limit, price=take_profit_price)



class MacrossOverLive():

    def __init__(self, data, symbol='EURUSD', timeframe=mt5.TIMEFRAME_M15):
        self.symbol = symbol
        self.timeframe = timeframe

    


    