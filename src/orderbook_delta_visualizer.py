import datetime
from collections import deque
from typing import Tuple

import dash
import pandas as pd
import pandas_ta as ta
import plotly.graph_objs as go
import plotly.io as pio
from dash import dcc, html
from dash.dependencies import Output, Input
from plotly.subplots import make_subplots

from ftx_websocket_client import FtxWebsocketClient


def get_bid_ask_and_delta(market: str) -> Tuple[float, float, float, float, float]:
    orderbook = ftx.get_orderbook(market)

    bid_price, bid_volume = orderbook["bids"][0]
    ask_price, ask_volume = orderbook["asks"][0]

    delta = bid_volume - ask_volume
    return bid_price, ask_price, bid_volume, ask_volume, delta


def update_deque_lists():
    timestamps.append(datetime.datetime.now())

    spot_bid_price, spot_ask_price, _, _, spot_delta = get_bid_ask_and_delta(SPOT_MARKET)
    spot_bids.append(spot_bid_price)
    spot_asks.append(spot_ask_price)
    spot_deltas.append(spot_delta)

    perp_bid_price, perp_ask_price, perp_bid_volume, perp_ask_volume, perp_delta = get_bid_ask_and_delta(PERP_FUTURE)
    perp_bids.append(perp_bid_price)
    perp_asks.append(perp_ask_price)
    perp_ask_volumes.append(perp_ask_volume)
    perp_bid_volumes.append(perp_bid_volume)
    perp_deltas.append(perp_delta)


app = dash.Dash(__name__)

app.layout = html.Div(
    [
        dcc.Graph(id='live-graph'),
        dcc.Interval(id='graph-update', interval=1000, n_intervals=0),
    ]
)


@app.callback(
    Output('live-graph', 'figure'),
    [Input('graph-update', 'n_intervals')]
)
def update_graph_scatter(_):
    update_deque_lists()

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                        subplot_titles=(
                            f"{SPOT_MARKET} price", f"{PERP_FUTURE} price",
                            f"{PERP_FUTURE} volume", f" Delta volume"))

    # Spot bids and asks
    fig.append_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(spot_bids),
            name='Spot Bids',
            mode='lines'
        ),
        row=1,
        col=1
    )
    fig.append_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(spot_asks),
            name='Spot Asks',
            mode='lines'
        ),
        row=1,
        col=1
    )

    # Perp bids and asks
    fig.append_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(perp_bids),
            name='Perp Bids',
            mode='lines'
        ),
        row=2,
        col=1
    )
    fig.append_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(perp_asks),
            name='Perp Asks',
            mode='lines'
        ),
        row=2,
        col=1
    )

    # Volumes
    fig.append_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(perp_ask_volumes),
            name='Perp Ask Volume',
            mode='lines+markers'
        ),
        row=3,
        col=1
    )
    fig.append_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(perp_bid_volumes),
            name='Perp Bid Volume',
            mode='lines+markers'
        ),
        row=3,
        col=1
    )

    # Bollinger Bands
    deltas = pd.Series(list(perp_deltas))
    bbands = ta.bbands(deltas, length=BBAND_LENGTH, std=BBAND_STD)

    # Delta
    fig.append_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(spot_deltas),
            name='Spot Delta',
            mode='lines+markers'
        ),
        row=4,
        col=1
    )
    fig.append_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(perp_deltas),
            name='Perp Delta',
            mode='lines+markers'
        ),
        row=4,
        col=1
    )

    if isinstance(bbands, pd.DataFrame):
        lower_bband = bbands.iloc[:, 0]
        upper_bband = bbands.iloc[:, 2]
        fig.append_trace(
            go.Scatter(
                x=list(timestamps),
                y=lower_bband,
                name='Lower BB',
                mode='lines'
            ),
            row=4,
            col=1
        )
        fig.append_trace(
            go.Scatter(
                x=list(timestamps),
                y=upper_bband,
                name='Upper BB',
                mode='lines'
            ),
            row=4,
            col=1
        )

    fig['layout'].update(
        title_text=f"{SPOT_MARKET} and {PERP_FUTURE} bid-ask orderbook at depth=1",
        xaxis=dict(range=[min(timestamps), max(timestamps)]),
        width=1400,
        height=800,
    )

    return fig


if __name__ == '__main__':
    # Set up parameters
    MAX_LENGTH = 100
    pio.templates.default = "plotly_dark"
    SPOT_MARKET = "BTC/USD"
    PERP_FUTURE = "BTC-PERP"
    BBAND_LENGTH = 20
    BBAND_STD = 3

    ftx = FtxWebsocketClient()

    # Initialize deque lists
    timestamps = deque(maxlen=MAX_LENGTH)
    spot_bids = deque(maxlen=MAX_LENGTH)
    spot_asks = deque(maxlen=MAX_LENGTH)
    perp_bids = deque(maxlen=MAX_LENGTH)
    perp_asks = deque(maxlen=MAX_LENGTH)
    spot_deltas = deque(maxlen=MAX_LENGTH)
    perp_deltas = deque(maxlen=MAX_LENGTH)
    perp_ask_volumes = deque(maxlen=MAX_LENGTH)
    perp_bid_volumes = deque(maxlen=MAX_LENGTH)

    update_deque_lists()

    app.run_server(use_reloader=True)
