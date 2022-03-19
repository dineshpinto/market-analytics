"""
MIT License

Copyright (c) 2022 Dinesh Pinto

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import datetime
import logging
import os
import sys
import time
from typing import Tuple

import pandas as pd
from tqdm import tqdm

from ftx_websocket_client import FtxWebsocketClient

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def get_bid_ask_and_delta(orderbook: dict) -> Tuple[float, float, float]:
    bid_price, bid_volume = orderbook["bids"][0]
    ask_price, ask_volume = orderbook["asks"][0]

    delta = bid_volume - ask_volume
    return bid_price, ask_price, delta


if __name__ == "__main__":
    NUM_POINTS = 3000  # no. on points
    TIME_DELTA = 5  # seconds between points

    ftx = FtxWebsocketClient()
    df = pd.DataFrame(
        columns=["time", "spot_bid_price", "spot_ask_price", "perp_bid_price",
                 "perp_ask_price", "spot_delta", "perp_delta"])
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y_%H-%M")
    logger.info(f"Starting query of FTX websocket with {NUM_POINTS=} and {TIME_DELTA=}")

    for idx in tqdm(range(NUM_POINTS)):
        try:
            orderbook_spot = ftx.get_orderbook("BTC/USD")
            orderbook_perp = ftx.get_orderbook("BTC-PERP")

            spot_bid_price, spot_ask_price, spot_delta = get_bid_ask_and_delta(orderbook_spot)
            perp_bid_price, perp_ask_price, perp_delta = get_bid_ask_and_delta(orderbook_perp)

            df.loc[idx] = [datetime.datetime.now(), spot_bid_price, spot_ask_price,
                           perp_bid_price, perp_ask_price, spot_delta, perp_delta]

            df.to_csv(os.path.join("..", "data", f"{timestamp}_delta.csv"))
        except Exception as exc:
            logger.exception(exc)
            pass
        time.sleep(TIME_DELTA)
