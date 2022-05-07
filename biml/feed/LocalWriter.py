import logging.config
from datetime import datetime
from typing import Dict, Any
import pandas as pd
from pathlib import Path


class LocalWriter:
    """
    Write feed to local dir
    """

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def on_candles(self, candles_dict: Dict[str, Dict[str, pd.DataFrame]]):
        """
        New candles have come, write them to local data folder. Files split by date.
        """

        for ticker in candles_dict:
            for interval in candles_dict[ticker]:
                candles = candles_dict[ticker][interval]
                # If candles are for diferent days, write each day to it's file
                dates = candles["close_time"].dt.date.unique()
                for date in dates:
                    file_path = self.get_file_name(ticker, interval, date)
                    logging.info(f"Writing to {file_path}")
                    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
                    # Write
                    candles.to_csv(file_path, header=not Path(file_path).exists(), mode='a')

    def get_file_name(self, ticker, interval: str, time: datetime):
        """
        Create file name for file data: folder/ticker/ticker_interval_time.csv
        """
        date = pd.to_datetime(time).date()
        return f"{self.data_dir}/{ticker}/{date}_{ticker}_{interval}.csv"