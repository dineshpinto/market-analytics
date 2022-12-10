from collections import OrderedDict

import numpy as np
from lmfit.models import Model


def make_antibunching_model(self, prefix=None):
    def antibunching(x: np.ndarray, n: float, a: float, b: float, tau0: float, tau1: float, tau2: float) \
            -> np.ndarray:
        """
        Fit to function
            f(x; n, a, tau0, tau1, tau2) =
                a * ((1 - (1+b) * exp(-|x-tau0|/tau1) + a * exp(-|x-tau0|/tau2)) * 1/n + 1 - 1/n)
        """
        return a * ((1 - (1 + b) * np.exp(-np.abs(x - tau0) / tau1) + b *
                     np.exp(-np.abs(x - tau0) / tau2)) * 1 / n + 1 - 1 / n)

    antibunching_model = Model(antibunching, independent_vars=['x'])
    params = antibunching_model.make_params()

    return antibunching_model, params


def estimate_antibunching_dip(self, x_axis, data, params):
    error = self._check_1D_input(x_axis=x_axis, data=data, params=params)

    params["n"].set(value=1)
    params["a"].set(value=1)
    params["b"].set(value=np.max(data) - np.min(data))
    params["tau0"].set(value=0)
    params["tau1"].set(value=20)
    params["tau2"].set(value=30)

    return error, params


def make_antibunching_fit(self, x_axis, data, estimator, units=None, add_params=None, **kwargs):
    model, params = self.make_antibunching_model()

    error, params = estimator(x_axis, data, params)

    params = self._substitute_params(initial_params=params,
                                     update_params=add_params)

    try:
        result = model.fit(data, x=x_axis, params=params, **kwargs)
    except:
        result = model.fit(data, x=x_axis, params=params, **kwargs)
        self.log.warning('The 1D antibunching fit did not work. Error '
                         'message: {0}\n'.format(result.message))

    # Write the parameters to allow human-readable output to be generated
    result_str_dict = OrderedDict()
    result.result_str_dict = result_str_dict

    return result
