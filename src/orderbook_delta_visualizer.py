import datetime
from collections import deque
from typing import Tuple

import dash
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from dash import dcc, html
from dash.dependencies import Output, Input
from plotly.subplots import make_subplots

from ftx_websocket_client import FtxWebsocketClient
from orderbook_delta_strategies import Position, Parameters


def get_bid_ask_and_delta(market: str) -> Tuple[float, float, float, float, float]:
    orderbook = ftx.get_orderbook(market)

    bid_price, bid_volume = orderbook["bids"][0]
    ask_price, ask_volume = orderbook["asks"][0]

    delta = bid_volume - ask_volume
    return bid_price, ask_price, bid_volume, ask_volume, delta


def update_deque_lists():
    """ Query websocket and update deque lists """
    try:
        spot_bid_price, spot_ask_price, spot_bid_volume, spot_ask_volume, spot_delta = get_bid_ask_and_delta(SPOT_MARKET)
        perp_bid_price, perp_ask_price, perp_bid_volume, perp_ask_volume, perp_delta = get_bid_ask_and_delta(PERP_FUTURE)
    except IndexError:
        # Catch errors from websocket and handle them by skipping over the point
        pass
    else:
        # If no error, append data into deque lists
        timestamps.append(datetime.datetime.now())

        spot_bids.append(spot_bid_price)
        spot_asks.append(spot_ask_price)
        spot_ask_volumes.append(spot_ask_volume)
        spot_bid_volumes.append(spot_bid_volume)
        spot_deltas.append(spot_delta)

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
    position.append(STRATEGY.strategy(perp_deltas=list(perp_deltas), spot_deltas=list(spot_deltas)))

    fig = make_subplots(rows=5, cols=1, shared_xaxes=True,
                        subplot_titles=(
                            f"{SPOT_MARKET} price", f"{SPOT_MARKET} volume", f"{PERP_FUTURE} price",
                            f"{PERP_FUTURE} volume", f" Delta volume (+ {STRATEGY})"))

    fig = STRATEGY.plot_strategy(timestamps=list(timestamps), fig=fig)

    # Spot bids and asks
    fig.add_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(spot_bids),
            name='Spot Bids',
            mode='lines',
            line=dict(color=px.colors.qualitative.Plotly[2])
        ),
        row=1,
        col=1
    )
    fig.add_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(spot_asks),
            name='Spot Asks',
            mode='lines',
            line=dict(color=px.colors.qualitative.Plotly[4])
        ),
        row=1,
        col=1
    )

    # Spot Volumes
    fig.add_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(spot_ask_volumes),
            name='Spot Ask Volume',
            mode='lines',
            line=dict(color=px.colors.qualitative.Plotly[6])
        ),
        row=2,
        col=1
    )
    fig.add_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(spot_bid_volumes),
            name='Spot Bid Volume',
            mode='lines',
            line=dict(color=px.colors.qualitative.Plotly[2])
        ),
        row=2,
        col=1
    )

    # Perp bids and asks
    fig.add_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(perp_bids),
            name='Perp Bids',
            mode='lines',
            line=dict(color=px.colors.qualitative.Plotly[2])
        ),
        row=3,
        col=1
    )
    fig.add_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(perp_asks),
            name='Perp Asks',
            mode='lines',
            line=dict(color=px.colors.qualitative.Plotly[4])
        ),
        row=3,
        col=1
    )

    # Volumes
    fig.add_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(perp_ask_volumes),
            name='Perp Ask Volume',
            mode='lines',
            line=dict(color=px.colors.qualitative.Plotly[6])
        ),
        row=4,
        col=1
    )
    fig.add_trace(
        go.Scatter(
            x=list(timestamps),
            y=list(perp_bid_volumes),
            name='Perp Bid Volume',
            mode='lines',
            line=dict(color=px.colors.qualitative.Plotly[2])
        ),
        row=4,
        col=1
    )

    __current_pos = None
    for idx, pos in enumerate(position):
        if pos == Position.LONG and __current_pos != Position.LONG:
            __current_pos = Position.LONG
            fig.add_vline(timestamps[idx + 1], line_color=px.colors.qualitative.Plotly[2],
                          line_dash="dot", row="all", col=1)
        elif pos == Position.SHORT and __current_pos != Position.SHORT:
            __current_pos = Position.SHORT
            fig.add_vline(timestamps[idx + 1], line_color=px.colors.qualitative.Plotly[6],
                          line_dash="dot", row="all", col=1)

    fig['layout'].update(
        title_text=f"{SPOT_MARKET} and {PERP_FUTURE} orderbook at depth=1",
        xaxis=dict(range=[min(timestamps), max(timestamps)]),
        autosize=True
    )

    return fig


if __name__ == '__main__':
    # Set up global params from Parameters dataclass
    pio.templates.default = Parameters.TEMPLATE
    SPOT_MARKET = Parameters.SPOT_MARKET
    PERP_FUTURE = Parameters.PERP_FUTURE
    STRATEGY = Parameters.STRATEGY
    MAX_VISIBLE_LENGTH = Parameters.MAX_VISIBLE_LENGTH

    # Initialize FTX websocket and deque lists
    ftx = FtxWebsocketClient()

    timestamps = deque(maxlen=MAX_VISIBLE_LENGTH)
    spot_bids = deque(maxlen=MAX_VISIBLE_LENGTH)
    spot_asks = deque(maxlen=MAX_VISIBLE_LENGTH)
    perp_bids = deque(maxlen=MAX_VISIBLE_LENGTH)
    perp_asks = deque(maxlen=MAX_VISIBLE_LENGTH)
    spot_deltas = deque(maxlen=MAX_VISIBLE_LENGTH)
    perp_deltas = deque(maxlen=MAX_VISIBLE_LENGTH)
    perp_ask_volumes = deque(maxlen=MAX_VISIBLE_LENGTH)
    perp_bid_volumes = deque(maxlen=MAX_VISIBLE_LENGTH)
    spot_bid_volumes = deque(maxlen=MAX_VISIBLE_LENGTH)
    spot_ask_volumes = deque(maxlen=MAX_VISIBLE_LENGTH)
    position = deque(maxlen=MAX_VISIBLE_LENGTH)

    update_deque_lists()

    app.run_server(use_reloader=True)
