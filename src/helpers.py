import pandas as pd
import numpy as np


def calculate_annualized_volatility(df: pd.DataFrame, window: int, num_windows_in_year: int) -> pd.DataFrame:
    """ Calculate volatility for a given dataframe and window size """
    annualization_factor = window / num_windows_in_year

    df['log_rtn_close'] = np.log(df['Close']).diff()
    df['real_volatility_close'] = np.sqrt(
        np.square(df['log_rtn_close']).rolling(window).sum() * annualization_factor)
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