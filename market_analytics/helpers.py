from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd


def calculate_annualized_volatility(
    df: pd.DataFrame, window: int, num_windows_in_year: int
) -> pd.DataFrame:
    """Calculate volatility for a given dataframe and window size"""
    annualization_factor = window / num_windows_in_year

    df["log_rtn_close"] = np.log(df["Close"]).diff()
    df["real_volatility_close"] = np.sqrt(
        np.square(df["log_rtn_close"]).rolling(window).sum() * annualization_factor
    )
    return df


def currency_formatter(x: float, _pos) -> str:
    if x >= 1e9:
        return f"${x / 1e9:1.1f}B"
    if 1e9 > x >= 1e6:
        return f"${x / 1e6:1.1f}M"
    if 1e6 > x >= 1e3:
        return f"${x / 1e3:1.0f}K"
    else:
        return f"${x:1.0f}"


def add_returns_pct(df: pd.DataFrame) -> pd.DataFrame:
    df["returns_pct"] = (df["close"] - df["open"]) / df["open"] * 100
    return df


def load_and_preprocess_data(
    path: Path, start_year: Optional[int] = None, add_return_pct: Optional[bool] = False
) -> pd.DataFrame:
    df = pd.read_csv(
        path, names=["timestamp", "open", "high", "low", "close", "volume", "trades"]
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df.set_index("timestamp", inplace=True, drop=True)
    if start_year:
        df = df[df.index.year > start_year]
    if add_return_pct:
        df = add_returns_pct(df)
    return df


def calculate_hpdr_bands(
    arr: np.ndarray, bins: int, hpdr_percents: list[float]
) -> list[float]:
    density_hist, bin_edges = np.histogram(arr, density=True, bins=bins)
    diff = np.diff(bin_edges)[0]
    density = np.array(
        [
            np.sum(density_hist[bins // 2 - idx : bins // 2 + idx]) * diff
            for idx in range(1, bins // 2 + 1)
        ]
    )
    hpdr_percent_ranges = []
    for percent in hpdr_percents:
        hpdr_percent_ranges.append(np.abs(density - percent).argmin() * diff)
    return hpdr_percent_ranges


def resample_data(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    return df.resample(**kwargs).agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
            "trades": "sum",
        }
    )
