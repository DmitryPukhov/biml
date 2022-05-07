import logging
import time
from datetime import timedelta
from typing import List

import numpy as np
import pandas as pd
from binance.spot import Spot as Client

from biml.feed.BaseFeed import BaseFeed
from biml.feed.TickerInfo import TickerInfo


class BinanceFeed(BaseFeed):
    """
    Binance price data feed. Read data from binance, provide pandas dataframes with that data
    """

    def __init__(self, spot_client: Client, tickers: List[TickerInfo]):
        super().__init__(tickers)
        self.spot_client: Client = spot_client

        # Read interval is a minimum candle interval
        # self.read_interval = min([pd.to_timedelta(interval) for interval in
        #                           itertools.chain([t.candle_intervals for t in self.tickers])])
        self.read_interval = timedelta(minutes=1)

    def run(self):
        """
        Read data periodically
        """
        while True:
            self.read()
            logging.info(f"Sleeping for {self.read_interval}")
            time.sleep(self.read_interval.total_seconds())

    def preprocess(self, df: pd.DataFrame) -> pd.DataFrame:
        df["open_time"] = pd.to_datetime(df["open_time"], unit='ms')
        df["close_time"] = pd.to_datetime(df["close_time"], unit='ms')
        return df

    def read(self):
        """
        Read data from binance to pandas
        """
        # Call binance for the data, read only new candles
        binance_time_millis = self.spot_client.time()['serverTime']
        binance_time = pd.to_datetime(binance_time_millis, unit='ms')
        logging.debug(f"Got binance server time {binance_time}")
        for ticker in self.tickers:
            for interval in ticker.candle_intervals:
                # Reset new candles
                # ticker.new_candles = {}
                if ticker.candle_last_times[interval] \
                        and (binance_time - ticker.candle_last_times[interval]) < pd.to_timedelta(interval):
                    # Time not elapsed for this interval, i.e. 15 minutes should pass from last time for M15
                    continue

                # Prepare params
                limit = ticker.candle_limits[interval]
                start_time = ticker.candle_last_times[interval]
                start_time_millis = start_time.to_datetime64() if start_time else None

                logging.debug(f"Read data from binance. ticker={ticker.ticker}, interval={interval}, "
                              f"start_time={start_time}, start_time_millis={start_time_millis} limit={limit}")
                # Call binance client
                new_binance_candles = self.spot_client.klines(symbol=ticker.ticker,
                                                              interval=interval,
                                                              limit=limit,
                                                              startTime=start_time_millis)
                # new_binance_candles = self.spot_client.klines(symbol=self.ticker,
                #                                               interval=interval,
                #                                               limit=limit)
                # Save last candle time millis for this ticker and interval
                new_candles = pd.DataFrame(data=new_binance_candles, columns=self.candle_columns)
                ticker.candle_last_times[interval] = pd.to_datetime(
                    max(start_time_millis, new_candles["close_time"].max()) if start_time_millis else new_candles[
                        'close_time'].max(), unit='ms')
                # Convert raw data to candles df
                new_candles = self.preprocess(new_candles)
                # Produce on_candles event if present
                for consumer in [c for c in self.consumers if hasattr(c, 'on_candles')]:
                    consumer.on_candles(ticker=ticker.ticker, interval=interval, candles=new_candles)
