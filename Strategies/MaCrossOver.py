import backtrader as bt


class MaCrossOverBt(bt.Strategy):
    params = (
         ('name', 'MaCrossOver'),
        ('maperiod', 10),
        ('maperiod2', 50),
        ('printlog', True),
        ('pip_value', 0.0001),  # Default pip value for most currency pairs
        ('stop_loss', 30),  # 10 pips stop loss
        ('take_profit', 100),  # 10 pips take profit
    )

    def log(self, txt, dt=None, doprint=True):
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
        self.trade_count = 0

    def stop(self):
        self.log(f'Final Value: {self.broker.get_cash():.2f}', doprint=True)
        self.log(f'ma: {self.params.maperiod}', doprint=True)
        self.log(f'Trade Count: {self.trade_count}')

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

    if not self.position:
        # Check for buy signal (SMA crosses above EMA)
        if self.sma[0] > self.ema[0] and self.sma[-1] <= self.ema[-1]:
            self.log(f'BUY CREATE, {self.dataclose[0]:.5f}')

            # Define stop loss and take profit prices for a buy order
            stop_loss_price = self.dataclose[0] - (self.params.stop_loss * self.params.pip_value)
            take_profit_price = self.dataclose[0] + (self.params.take_profit * self.params.pip_value)

            self.log(f'BUY Stop Loss: {stop_loss_price:.5f}, Take Profit: {take_profit_price:.5f}', doprint=True)

            # Place bracket order (stop loss and take profit) for the buy order
            self.order = self.buy_bracket(
                stopprice=stop_loss_price,  # Stop-loss
                limitprice=take_profit_price  # Take-profit
            )
            self.trade_count += 1

        # Check for sell signal (SMA crosses below EMA)
        elif self.sma[0] < self.ema[0] and self.sma[-1] >= self.ema[-1]:
            self.log(f'SELL CREATE, {self.dataclose[0]:.5f}')

            # Define stop loss and take profit prices for a sell order
            stop_loss_price = self.dataclose[0] + (self.params.stop_loss * self.params.pip_value)
            take_profit_price = self.dataclose[0] - (self.params.take_profit * self.params.pip_value)

            self.log(f'SELL Stop Loss: {stop_loss_price:.5f}, Take Profit: {take_profit_price:.5f}', doprint=True)

            # Place bracket order (stop loss and take profit) for the sell order
            self.order = self.sell_bracket(
                stopprice=stop_loss_price,  # Stop-loss
                limitprice=take_profit_price  # Take-profit
            )
            self.trade_count += 1

