import logging.config
from binance.spot import Spot as Client
from datetime import datetime, timedelta
import pandas as pd


class BaseFeed:
    """
    Base class for price data feed. Read data, provide pandas dataframes with that data
    """

    def __init__(self, spot_client: Client, ticker: str):
        self.spot_client: Client = spot_client
        self.ticker = ticker

        # Fast and medium candles
        self.candle_fast_interval = "1m"
        self.candle_medium_interval = "15m"
        self.candle_fast_limit = 15
        self.candle_medium_limit = 20
        # Column names of binance candle data
        self.candle_columns = ["open_time", "open", "high", "low", "close", "vol", "close_time", "quote_asset_volume",
                               "number_of_trades", " taker_buy_base_asset_volume", "taker_buy_quote_asset_volume",
                               "ignore"]
        # Pandas dataframes to hold data
        self.candles_fast = pd.DataFrame(columns=self.candle_columns)
        self.candles_medium = pd.DataFrame(columns=self.candle_columns)

        logging.info(
            f"Feed initialized. candle_fast_interval: {self.candle_fast_interval}, candle_fast_limit:{self.candle_fast_limit}"
            f"candle_medium_interval: {self.candle_medium_interval}, candle_medium_limit:{self.candle_medium_limit},\n"
            f"candle_columns: {self.candle_columns},\n")

    def read(self):
        """
        Read data to pandas
        """
        pass