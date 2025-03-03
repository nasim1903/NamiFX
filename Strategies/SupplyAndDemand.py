import backtrader as bt

class TrendFollowingStrategy(bt.Strategy):
    params = (
        ('ema_period', 80),     # Approximate 1-hour EMA for trend detection
        ('stoch_k', 14),        # Stochastic K period
        ('stoch_d', 3),         # Stochastic D period
        ('stoch_smooth', 3),    # Smoothing factor for stochastic
        ('atr_period', 14),     # ATR period for SL/TP calculation
        ('atr_mult_sl', 1.5),   # SL multiplier
        ('atr_mult_tp', 10),     # TP multiplier for 1:2 risk-reward
    )

    def __init__(self):
        self.ema = bt.indicators.EMA(period=self.params.ema_period)
        self.stoch = bt.indicators.Stochastic(
            period=self.params.stoch_k, period_dfast=self.params.stoch_d, period_dslow=self.params.stoch_smooth
        )
        self.atr = bt.indicators.ATR(period=self.params.atr_period)
        self.order = None
        self.trade_count = 0

    def notify_order(self, order):
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
        
        price = self.data.close[0]
        atr_value = self.atr[0]
        trend_up = price > self.ema[0]
        trend_down = price < self.ema[0]
        
        # Long entry conditions
        if not self.position and trend_up and self.stoch.percK[0] < 20 and self.stoch.percK[-1] < self.stoch.percK[0]:
            stop_loss = price - (self.params.atr_mult_sl * atr_value)
            take_profit = price + (self.params.atr_mult_tp * atr_value)
            self.order = self.buy_bracket(stopprice=stop_loss, limitprice=take_profit)
            self.trade_count += 1
            
        # Short entry conditions
        elif not self.position and trend_down and self.stoch.percK[0] > 80 and self.stoch.percK[-1] > self.stoch.percK[0]:
            stop_loss = price + (self.params.atr_mult_sl * atr_value)
            take_profit = price - (self.params.atr_mult_tp * atr_value)
            self.order = self.sell_bracket(stopprice=stop_loss, limitprice=take_profit)
            self.trade_count += 1
    
    def log(self, txt, dt=None, doprint=False):
        if doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print(f'{dt.isoformat()}, {txt}')
    
    def stop(self):
        self.log(f'Final Account Value: {self.broker.get_cash():,.2f}', doprint=True)
        self.log(f'Total Trades Executed: {self.trade_count}', doprint=True)
