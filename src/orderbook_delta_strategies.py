from abc import ABC, abstractmethod
from enum import Enum

import pandas as pd
import pandas_ta as ta
import plotly.graph_objects as go


class Position(Enum):
    """ Enum to hold all possible positions """
    LONG = 1
    SHORT = -1
    NONE = 0


class BaseStrategy(ABC):
    """ Abstract class to define all strategies """

    @abstractmethod
    def strategy(self, **kwargs) -> Position:
        """ Method containing raw strategy, must return a Position """
        raise NotImplementedError

    @abstractmethod
    def plot_strategy(self, **kwargs) -> go.Figure:
        """ Method containing plotting logic, must return a Plotly graph object """
        raise NotImplementedError

    @abstractmethod
    def __repr__(self) -> str:
        raise NotImplementedError


class BollingerBandStrategy(BaseStrategy):
    def __init__(self, bband_length: int, bband_std: float):
        self.bband_length = bband_length
        self.bband_std = bband_std
        self.delta_prod = None
        self.lower_bband = None
        self.upper_bband = None

    def __repr__(self) -> str:
        return f"Delta Product Bollinger Band Strategy"

    def strategy(self, perp_deltas: list, spot_deltas: list) -> Position:
        self.delta_prod = pd.Series(perp_deltas) * pd.Series(spot_deltas)

        bbands = ta.bbands(self.delta_prod, length=self.bband_length, std=self.bband_std)

        if isinstance(bbands, pd.DataFrame):
            self.lower_bband = bbands.iloc[:, 0]
            self.upper_bband = bbands.iloc[:, 2]

            if self.delta_prod.values[-1] > self.upper_bband.values[-1]:
                return Position.SHORT
            elif self.delta_prod.values[-1] < self.lower_bband.values[-1]:
                return Position.LONG
        return Position.NONE

    def plot_strategy(self, timestamps: list, fig: go.Figure) -> go.Figure:
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=self.delta_prod,
                name='Spot * Perp Delta',
                mode='lines+markers',
                marker=dict(symbol="circle")
            ),
            row=5,
            col=1
        )

        if isinstance(self.lower_bband, pd.Series) and isinstance(self.upper_bband, pd.Series):
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=self.lower_bband,
                    name='Lower BB',
                    mode='lines'
                ),
                row=5,
                col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=list(timestamps),
                    y=self.upper_bband,
                    name='Upper BB',
                    mode='lines'
                ),
                row=5,
                col=1
            )
        return fig
