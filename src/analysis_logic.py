from __future__ import annotations

import logging
from enum import Enum
from typing import Tuple, TYPE_CHECKING

import numpy as np
import pandas as pd

from qudi_fit_logic import FitLogic

if TYPE_CHECKING:
    from lmfit.model import ModelResult

logging.basicConfig(format='%(name)s :: %(levelname)s :: %(message)s', level=logging.INFO)


class FitMethods(Enum):
    decayexponential: str = "decayexponential"
    biexponential: str = "biexponential"
    decayexponentialstretched: str = "decayexponentialstretched"
    gaussian: str = "gaussian"
    gaussiandouble: str = "gaussiandouble"
    gaussianlinearoffset: str = "gaussianlinearoffset"
    hyperbolicsaturation: str = "hyperbolicsaturation"
    linear: str = "linear"
    lorentzian: str = "lorentzian"
    lorentziandouble: str = "lorentziandouble"
    lorentziantriple: str = "lorentziantriple"
    sine: str = "sine"
    sinedouble: str = "sinedouble"
    sinedoublewithexpdecay: str = "sinedoublewithexpdecay"
    sinedoublewithtwoexpdecay: str = "sinedoublewithtwoexpdecay"
    sineexponentialdecay: str = "sineexponentialdecay"
    sinestretchedexponentialdecay: str = "sinestretchedexponentialdecay"
    sinetriple: str = "sinetriple"
    sinetriplewithexpdecay: str = "sinetriplewithexpdecay"
    sinetriplewiththreeexpdecay: str = "sinetriplewiththreeexpdecay"
    twoDgaussian: str = "twoDgaussian"
    antibunching: str = "antibunching"


class AnalysisLogic(FitLogic):
    def __init__(self):
        super().__init__()
        self.log = logging.getLogger(__name__)

    def perform_fit(
            self,
            x: pd.Series,
            y: pd.Series,
            fit_function: str | FitMethods,
            estimator: str = "generic",
            dims: str = "1d") -> Tuple[np.ndarray, np.ndarray, ModelResult]:
        """
        Fits available:
            | Dimension | Fit                           |
            |-----------|-------------------------------|
            | 1d        | decayexponential              |
            |           | biexponential                 |
            |           | decayexponentialstretched     |
            |           | gaussian                      |
            |           | gaussiandouble                |
            |           | gaussianlinearoffset          |
            |           | hyperbolicsaturation          |
            |           | linear                        |
            |           | lorentzian                    |
            |           | lorentziandouble              |
            |           | lorentziantriple              |
            |           | sine                          |
            |           | sinedouble                    |
            |           | sinedoublewithexpdecay        |
            |           | sinedoublewithtwoexpdecay     |
            |           | sineexponentialdecay          |
            |           | sinestretchedexponentialdecay |
            |           | sinetriple                    |
            |           | sinetriplewithexpdecay        |
            |           | sinetriplewiththreeexpdecay   |
            | 2d        | twoDgaussian                  |
        Estimators:
            - generic
            - dip
        """

        if isinstance(x, pd.Series) or isinstance(x, pd.Index):
            x = x.to_numpy()
        if isinstance(y, pd.Series):
            y = y.to_numpy()
        if isinstance(fit_function, FitMethods):
            fit_function = fit_function.name

        fit = {dims: {'default': {'fit_function': fit_function, 'estimator': estimator}}}
        user_fit = self.validate_load_fits(fit)

        use_settings = {}
        for key in user_fit[dims]["default"]["parameters"].keys():
            use_settings[key] = False
        user_fit[dims]["default"]["use_settings"] = use_settings

        fc = self.make_fit_container("test", dims)
        fc.set_fit_functions(user_fit[dims])
        fc.set_current_fit("default")
        fc.use_settings = None
        fit_x, fit_y, result = fc.do_fit(x, y)
        return fit_x, fit_y, result

    def get_all_fits(self) -> Tuple[list, list]:
        one_d_fits = list(self.fit_list['1d'].keys())
        two_d_fits = list(self.fit_list['2d'].keys())
        self.log.info(f"1d fits: {one_d_fits}\n2d fits: {two_d_fits}")
        return one_d_fits, two_d_fits

    @staticmethod
    def analyse_mean(
            laser_data: np.ndarray,
            signal_start: float = 0.0,
            signal_end: float = 200e-9,
            bin_width: float = 1e-9) -> Tuple[np.ndarray, np.ndarray]:
        # Get number of lasers
        num_of_lasers = laser_data.shape[0]

        if not isinstance(bin_width, float):
            return np.zeros(num_of_lasers), np.zeros(num_of_lasers)

        # Convert the times in seconds to bins (i.e. array indices)
        signal_start_bin = round(signal_start / bin_width)
        signal_end_bin = round(signal_end / bin_width)

        # initialize data arrays for signal and measurement error
        signal_data = np.empty(num_of_lasers, dtype=float)
        error_data = np.empty(num_of_lasers, dtype=float)

        # loop over all laser pulses and analyze them
        for ii, laser_arr in enumerate(laser_data):
            # calculate the mean of the data in the signal window
            signal = laser_arr[signal_start_bin:signal_end_bin].mean()
            signal_sum = laser_arr[signal_start_bin:signal_end_bin].sum()
            signal_error = np.sqrt(signal_sum) / (signal_end_bin - signal_start_bin)

            # Avoid numpy C type variables overflow and NaN values
            if signal < 0 or signal != signal:
                signal_data[ii] = 0.0
                error_data[ii] = 0.0
            else:
                signal_data[ii] = signal
                error_data[ii] = signal_error

        return signal_data, error_data

    @staticmethod
    def analyse_mean_reference(
            laser_data: np.ndarray,
            signal_start: float = 0.0,
            signal_end: float = 200e-9,
            norm_start: float = 300e-9,
            norm_end: float = 500e-9,
            bin_width: float = 1e-9) -> Tuple[np.ndarray, np.ndarray]:
        """
        This method takes the mean of the signal window.
        It then does not divide by the background window to normalize
        but rather substracts the background window to generate the output.
        """
        # Get number of lasers
        num_of_lasers = laser_data.shape[0]

        if not isinstance(bin_width, float):
            return np.zeros(num_of_lasers), np.zeros(num_of_lasers)

        # Convert the times in seconds to bins (i.e. array indices)
        signal_start_bin = round(signal_start / bin_width)
        signal_end_bin = round(signal_end / bin_width)
        norm_start_bin = round(norm_start / bin_width)
        norm_end_bin = round(norm_end / bin_width)

        # initialize data arrays for signal and measurement error
        signal_data = np.empty(num_of_lasers, dtype=float)
        error_data = np.empty(num_of_lasers, dtype=float)

        # loop over all laser pulses and analyze them
        for ii, laser_arr in enumerate(laser_data):
            # calculate the sum and mean of the data in the normalization window
            tmp_data = laser_arr[norm_start_bin:norm_end_bin]
            reference_sum = np.sum(tmp_data)
            reference_mean = (reference_sum / len(tmp_data)) if len(tmp_data) != 0 else 0.0

            # calculate the sum and mean of the data in the signal window
            tmp_data = laser_arr[signal_start_bin:signal_end_bin]
            signal_sum = np.sum(tmp_data)
            signal_mean = (signal_sum / len(tmp_data)) if len(tmp_data) != 0 else 0.0

            signal_data[ii] = signal_mean - reference_mean

            # calculate with respect to gaussian error 'evolution'
            error_data[ii] = signal_data[ii] * np.sqrt(1 / abs(signal_sum) + 1 / abs(reference_sum))

        return signal_data, error_data

    @staticmethod
    def analyse_mean_norm(
            laser_data: np.ndarray,
            signal_start: float = 0.0,
            signal_end: float = 200e-9,
            norm_start: float = 300e-9,
            norm_end=500e-9,
            bin_width: float = 1e-9) -> Tuple[np.ndarray, np.ndarray]:
        # Get number of lasers
        num_of_lasers = laser_data.shape[0]

        if not isinstance(bin_width, float):
            return np.zeros(num_of_lasers), np.zeros(num_of_lasers)

        # Convert the times in seconds to bins (i.e. array indices)
        signal_start_bin = round(signal_start / bin_width)
        signal_end_bin = round(signal_end / bin_width)
        norm_start_bin = round(norm_start / bin_width)
        norm_end_bin = round(norm_end / bin_width)

        # initialize data arrays for signal and measurement error
        signal_data = np.empty(num_of_lasers, dtype=float)
        error_data = np.empty(num_of_lasers, dtype=float)

        # loop over all laser pulses and analyze them
        for ii, laser_arr in enumerate(laser_data):
            # calculate the sum and mean of the data in the normalization window
            tmp_data = laser_arr[norm_start_bin:norm_end_bin]
            reference_sum = np.sum(tmp_data)
            reference_mean = (reference_sum / len(tmp_data)) if len(tmp_data) != 0 else 0.0

            # calculate the sum and mean of the data in the signal window
            tmp_data = laser_arr[signal_start_bin:signal_end_bin]
            signal_sum = np.sum(tmp_data)
            signal_mean = (signal_sum / len(tmp_data)) if len(tmp_data) != 0 else 0.0

            # Calculate normalized signal while avoiding division by zero
            if reference_mean > 0 and signal_mean >= 0:
                signal_data[ii] = signal_mean / reference_mean
            else:
                signal_data[ii] = 0.0

            # Calculate measurement error while avoiding division by zero
            if reference_sum > 0 and signal_sum > 0:
                # calculate with respect to gaussian error 'evolution'
                error_data[ii] = signal_data[ii] * np.sqrt(1 / signal_sum + 1 / reference_sum)
            else:
                error_data[ii] = 0.0

        return signal_data, error_data
