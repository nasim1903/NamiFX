import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from Data import dataLoader as dl
import pandas as pd
import backtrader as bt
import MetaTrader5 as mt5

class CrashBoomStrategy(bt.Strategy):
    params = (
        ('printlog', True),
        ('bollinger_period', 20),  
        ('devfactor', 2),          
        ('ema_trend_period', 400), 
        ('ema_signal_period', 5),  
        ('atr_period', 14),        
        ('atr_mult', 1.5),         
        ('profit_mult', 2),        
        ('trail_trigger', 10),     # Move SL to breakeven after 10 pips
        ('trail_atr_mult', 1.5),   # ATR multiplier for trailing SL
        ('lots', 0.01),            
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function for this strategy '''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.trade_count = 0  
        self.trailing_stop = None  

        # Higher timeframe indicators (Trend)
        self.ema400 = bt.indicators.EMA(period=self.params.ema_trend_period)
        self.bollinger = bt.indicators.BollingerBands(period=self.params.bollinger_period, devfactor=self.params.devfactor)

        # Lower timeframe indicators (Entry)
        self.ema5 = bt.indicators.EMA(period=self.params.ema_signal_period)
        self.atr = bt.indicators.ATR(period=self.params.atr_period)

    def stop(self):
        """Print strategy summary when backtest ends."""
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
        """Handle order execution updates."""
        if order.status in [order.Submitted, order.Accepted]:
            return
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f'BUY EXECUTED, Price: {order.executed.price:.5f}')
                self.entry_price = order.executed.price  # Store entry price
            elif order.issell():
                self.log(f'SELL EXECUTED, Price: {order.executed.price:.5f}')
                self.entry_price = order.executed.price  
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.order = None

    def next(self):
        """Define trade logic on each new candle."""
        if self.order:
            return  

        price = self.dataclose[0]
        atr_value = self.atr[0]
        lower_band = self.bollinger.lines.bot[0]
        upper_band = self.bollinger.lines.top[0]
        mid_band = self.bollinger.lines.mid[0]

        # Trend Detection (Higher Timeframe)
        if price > self.ema400[0] and price < upper_band:
            trend = "UP_TREND"
        elif price < self.ema400[0] and price > lower_band:
            trend = "DOWN_TREND"
        else:
            trend = "CONSOLLIDATING"

        # Entry Conditions (Lower Timeframe)
        if not self.position:
            if trend == "UP_TREND" and self.ema5[-1] < mid_band and self.ema5[0] > mid_band:
                stop_loss = lower_band - (self.params.atr_mult * atr_value)
                take_profit = price + (self.params.profit_mult * (price - stop_loss))

                self.order = self.buy_bracket(
                    stopprice=stop_loss,  
                    limitprice=take_profit  
                )
                self.trade_count += 1
                self.trailing_stop = stop_loss  # Set initial SL
                self.log(f'Trade {self.trade_count}: BUY at {price}, SL: {stop_loss}, TP: {take_profit}')

            elif trend == "DOWN_TREND" and self.ema5[-1] > mid_band and self.ema5[0] < mid_band:
                stop_loss = upper_band + (self.params.atr_mult * atr_value)
                take_profit = price - (self.params.profit_mult * (stop_loss - price))

                self.order = self.sell_bracket(
                    stopprice=stop_loss,  
                    limitprice=take_profit  
                )
                self.trade_count += 1
                self.trailing_stop = stop_loss  # Set initial SL
                self.log(f'Trade {self.trade_count}: SELL at {price}, SL: {stop_loss}, TP: {take_profit}')
        
        # **Implement Trailing Stop**
        elif self.position:
            if self.position.size > 0:  # Long Position
                profit_pips = (price - self.entry_price) * 10000  
                if profit_pips > self.params.trail_trigger:  
                    new_sl = max(self.trailing_stop, self.entry_price)  # Move SL to breakeven
                    new_sl = max(new_sl, price - (self.params.trail_atr_mult * atr_value))  # Trail by ATR
                    if new_sl > self.trailing_stop:  # Only update if it's moving in favor
                        self.trailing_stop = new_sl
                        self.log(f'Trailing SL moved to {new_sl:.5f}')
                        self.sell(exectype=bt.Order.Stop, price=self.trailing_stop)  

            elif self.position.size < 0:  # Short Position
                profit_pips = (self.entry_price - price) * 10000  
                if profit_pips > self.params.trail_trigger:  
                    new_sl = min(self.trailing_stop, self.entry_price)  
                    new_sl = min(new_sl, price + (self.params.trail_atr_mult * atr_value))  
                    if new_sl < self.trailing_stop:  
                        self.trailing_stop = new_sl
                        self.log(f'Trailing SL moved to {new_sl:.5f}')
                        self.buy(exectype=bt.Order.Stop, price=self.trailing_stop)  
