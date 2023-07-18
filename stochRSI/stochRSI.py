from datetime import datetime
import backtrader as bt
import pandas as pd


class StochRSI(bt.Indicator):
    lines = ('stochrsi',)
    params = {
        'period': 14
    }

    def __init__(self):
        period = self.params.period
        rsi = bt.indicators.RSI(self.data, period=period)
        maxrsi = bt.indicators.Highest(rsi, period=period)
        minrsi = bt.indicators.Lowest(rsi, period=period)
        self.lines.stochrsi = (rsi - minrsi) / (maxrsi - minrsi)


class StochRSIStrategy(bt.Strategy):
    def __init__(self):
        self.stochrsi_indicator = StochRSI()
        self.order_exist = False

    def next(self):
        previous_stochrsi = self.stochrsi_indicator.lines.stochrsi[-1]
        current_stochrsi = self.stochrsi_indicator.lines.stochrsi[0]
        buy_signal = previous_stochrsi < current_stochrsi and current_stochrsi < 0.2
        sell_signal = previous_stochrsi > current_stochrsi and current_stochrsi > 0.8

        if buy_signal and not self.order_exist:
            #print(buy_signal)
            #print(f'BUY: {current_stochrsi}')
            #self.buy()
            self.order = self.order_target_percent(target=1)
            self.order_exist = True

        if sell_signal and self.order_exist:
            #print(f'SELL: {current_stochrsi}')
            self.order= self.order_target_percent(target=-1)
            self.order_exist = False


if __name__ == '__main__':
    cerebro = bt.Cerebro()
    cerebro.broker.setcash(100000)
    print(f'Starting value: {cerebro.broker.getvalue()}')

    data = pd.read_excel(r'/home/baichen/Downloads/ibtrade/NVDA_10Y_1day.xlsx',index_col=0,parse_dates=["Date"])
    data_parsed=bt.feeds.PandasData(dataname=data,datetime=None,open=0,high=1,low=2,close=3,volume=4,openinterest=-1)
    cerebro.adddata(data_parsed)
    cerebro.addstrategy(StochRSIStrategy)

    cerebro.run()
    cerebro.plot(style = 'candle')

    print(f'Final value: {cerebro.broker.getvalue()}')

