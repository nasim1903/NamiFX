import backtrader as bt
import sys
import os
import datetime
import MetaTrader5 as mt5
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data import dataLoader as dl

class SwingFailurePattern(bt.Indicator):
    params = (('lookback', 10),)  # Number of bars to check for swing points

    lines = ('sfp_signal', 'swing_high', 'swing_low')  # Indicator lines

    def __init__(self):
        self.addminperiod(self.p.lookback + 1)  # Ensure enough data

    def next(self):
        lookback = self.p.lookback
        high_window = self.data.high.get(size=lookback)
        low_window = self.data.low.get(size=lookback)

        if len(high_window) < lookback:
            return  # Not enough data

        # Identify Swing High
        if self.data.high[0] < max(high_window[:-1]):
            self.lines.swing_high[0] = max(high_window[:-1])
        else:
            self.lines.swing_high[0] = float('nan')

        # Identify Swing Low
        if self.data.low[0] > min(low_window[:-1]):
            self.lines.swing_low[0] = min(low_window[:-1])
        else:
            self.lines.swing_low[0] = float('nan')

        # Detect Bearish Swing Failure (New high but closes below previous swing high)
        if self.data.high[0] > max(high_window[:-1]) and self.data.close[0] < max(high_window[:-1]):
            self.lines.sfp_signal[0] = 1  # Bearish SFP Signal
        # Detect Bullish Swing Failure (New low but closes above previous swing low)
        elif self.data.low[0] < min(low_window[:-1]) and self.data.close[0] > min(low_window[:-1]):
            self.lines.sfp_signal[0] = -1  # Bullish SFP Signal
        else:
            self.lines.sfp_signal[0] = 0  # No Signal

class SFPStrategy(bt.Strategy):
    def __init__(self):
        self.sfp = SwingFailurePattern(self.data)
        self.order = None
        self.trade_count = 0  
        self.dataclose = self.datas[0].close

        # Higher timeframe indicators (Trend)
        self.ema200 = bt.indicators.EMA(period=200)
        
        # Add ATR indicator (you can change the period if necessary)
        self.atr = bt.indicators.ATR(self.data, period=14)  # ATR with a period of 14

    def stop(self):
        self.log(f'Final Value: {self.broker.get_cash():.2f}', doprint=True)
        self.log(f'Trade Count: {self.trade_count}')

    def log(self, txt, dt=None, doprint=True):
        ''' Logging function for this strategy '''
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

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
        """Define trade logic on each new candle."""

        if not self.position:
            # Bearish SFP
            if self.sfp.sfp_signal[0] == 1 and self.dataclose[0] < self.ema200[0]:
                # Use ATR to define stop loss and take profit
                atr_value = self.atr[0]  # Get the ATR value for the current bar
                stop_loss = self.dataclose[0] + (1.5 * atr_value)  # 1.5 * ATR above the current price
                take_profit = self.dataclose[0] - (2 * atr_value)  # 3 * ATR below the current price

                self.order = self.sell_bracket(
                    stopprice=stop_loss,
                    limitprice=take_profit
                )

                self.trade_count += 1

            # Bullish SFP
            elif self.sfp.sfp_signal[0] == -1 and self.dataclose[0] > self.ema200[0]:
                # Use ATR to define stop loss and take profit
                atr_value = self.atr[0]  # Get the ATR value for the current bar
                stop_loss = self.dataclose[0] - (1.5 * atr_value)  # 1.5 * ATR below the current price
                take_profit = self.dataclose[0] + (2 * atr_value)  # 3 * ATR above the current price

                self.order = self.buy_bracket(
                    stopprice=stop_loss,
                    limitprice=take_profit
                )

                self.trade_count += 1
        