import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data import dataLoader as dl
import pandas as pd
import backtrader as bt
import MetaTrader5 as mt5


class MeanReversionStrategy(bt.Strategy):
    params = (
        ('printlog', False),
        ('bollinger_period', 20),  # Bollinger Bands period
        ('devfactor', 2),          # Standard deviation factor
        ('atr_period', 14),        # ATR period
        ('atr_mult', 1.5),         # ATR multiplier for stop-loss
        ('profit_mult', 2),      # Profit target multiplier
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy '''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.bollinger = bt.indicators.BollingerBands(period=self.params.bollinger_period, devfactor=self.params.devfactor)
        self.atr = bt.indicators.ATR(period=self.params.atr_period)
        self.trade_count = 0  # Initialize trade counter

    def stop(self):
        self.log("=" * 50, doprint=True)
        self.log(" STRATEGY SUMMARY ", doprint=True)
        self.log("=" * 50, doprint=True)
        
        self.log(f"Final Account Value : {self.broker.get_cash():,.2f}", doprint=True)
        self.log(f"Total Trades Executed: {self.trade_count}", doprint=True)
        
        self.log("-" * 50, doprint=True)
        self.log(" Strategy Parameters ", doprint=True)
        self.log("-" * 50, doprint=True)

        for param in self.params._getkeys():
            self.log(f"{param.replace('_', ' ').title():<20}: {getattr(self.params, param)}", doprint=True)

        self.log("=" * 50, doprint=True)



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

        if self.order:
            return
        
        close = self.dataclose[0]
        
        atr_value = self.atr[0]
        lower_band = self.bollinger.lines.bot[0]
        upper_band = self.bollinger.lines.top[0]
        mid_band = self.bollinger.lines.mid[0]
        close = self.data.close[0]
        
        if not self.position:
            if close < lower_band:
                stop_loss = close - (self.params.atr_mult * atr_value)
                take_profit = close + (self.params.profit_mult * atr_value)

                self.order = self.buy_bracket(
                    stopprice=stop_loss,  # Stop-loss
                    limitprice=take_profit  # Take-profit
                )
                self.trade_count += 1

                # print(f'Trade {self.trade_count}: BUY at {close}, LOWER-BAND:, {lower_band}, SL: {stop_loss}, TP: {take_profit}')

            elif close > upper_band:
                stop_loss = close + (self.params.atr_mult * atr_value)
                take_profit = close - (self.params.profit_mult * atr_value)

                self.order = self.sell_bracket(
                    stopprice=stop_loss,  # Stop-loss
                    limitprice=take_profit  # Take-profit
                )
                self.trade_count += 1

                # print(f'Trade {self.trade_count}: SELL at {close}, UPPER-BAND:, {upper_band}, SL: {stop_loss}, TP: {take_profit}')