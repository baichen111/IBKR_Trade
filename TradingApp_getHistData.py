#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 13:18:47 2023

@author: baichen
"""

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
import pandas as pd

# from ibapi.execution import *
import threading
import time


class TradingApp_HistData(EWrapper, EClient):
    def __init__(self, duration, candle_Size):
        self.duration = duration
        self.candle_Size = candle_Size

        EClient.__init__(self, self)

        # establish connection with TWS
        self.connect("127.0.0.1", port=7497, clientId=2)
        connThread = threading.Thread(target=self.__websocket_conn, daemon=True)
        connThread.start()
        time.sleep(2)

        self.data = {}
        self.data_event = threading.Event()

        self.df_data = {}
        self.duration = duration
        self.candle_Size = candle_Size

    def __websocket_conn(self):
        print("run")
        self.run()

    def error(self, reqId, errorCode, errorString):
        print("Error {} {} {}".format(reqId, errorCode, errorString))

    def historicalData(self, reqId, bar):
        if reqId not in self.data:
            self.data[reqId] = [
                {
                    "Date": bar.date,
                    "Open": bar.open,
                    "High": bar.high,
                    "Low": bar.low,
                    "Close": bar.close,
                    "Volume": bar.volume,
                }
            ]
        else:
            self.data[reqId].append(
                {
                    "Date": bar.date,
                    "Open": bar.open,
                    "High": bar.high,
                    "Low": bar.low,
                    "Close": bar.close,
                    "Volume": bar.volume,
                }
            )
        print(
            "reqID:{}, date:{}, open:{}, high:{}, low:{}, close:{}, volume:{}".format(
                reqId, bar.date, bar.open, bar.high, bar.low, bar.close, bar.volume
            )
        )

    def historicalDataEnd(self, reqId, start, end):
        super().historicalDataEnd(reqId, start, end)
        print("HistoricalDataEnd. ReqId:", reqId, "from", start, "to", end)
        self.data_event.set()

    ############################################
    def __stkContract(self, symbol, secType="STK", currency="USD", exchange="ISLAND"):
        contract = Contract()
        contract.symbol = symbol
        contract.secType = secType
        contract.currency = currency
        contract.exchange = exchange
        return contract

    def __historicalData(self, req_id, contract):
        self.reqHistoricalData(
            reqId=req_id,
            contract=contract,
            endDateTime="",
            durationStr=self.duration,
            barSizeSetting=self.candle_Size,
            whatToShow="ADJUSTED_LAST",
            useRTH=1,
            formatDate=1,
            keepUpToDate=0,
            chartOptions=[],
        )

    def getHistData(self, symbols: list, saveToExcel: int):  # saveToExcel : 0 or 1
        for sym in symbols:
            self.data_event.clear()  # reset data download event
            self.__historicalData(symbols.index(sym), self.__stkContract(sym))
            self.data_event.wait()  # event waiting for data downloading to complete
            self.df_data[sym] = pd.DataFrame(self.data[symbols.index(sym)])
            self.df_data[sym].set_index("Date", inplace=True)

            if saveToExcel:
                print("Saving down to disk")
                self.df_data[sym].to_excel(
                    r"{}_{}_{}.xlsx".format(
                        sym,
                        self.duration.replace(" ", ""),
                        self.candle_Size.replace(" ", ""),
                    )
                )
        return self.df_data


if __name__ == "__main__":
    trade_app = TradingApp_HistData("10 D", "15 mins")
    df = trade_app.getHistData(["META", "AMZN", "AAPL"], 1)
    print(df)
