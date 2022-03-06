import os
import logging
import pandas as pd
import yaml
from prophet import Prophet
import json
from prophet.serialize import model_from_json

from src.d00_utils.const import *
from src.d00_utils.utils import get_filepath

from matplotlib import pyplot as plt
from matplotlib.dates import (
    MonthLocator,
    num2date,
    AutoDateLocator,
    AutoDateFormatter,
)
from matplotlib.ticker import FuncFormatter

from pandas.plotting import deregister_matplotlib_converters
deregister_matplotlib_converters()

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)




def plot(
    fcst, ax=None, uncertainty=True, plot_cap=True, xlabel='ds', ylabel='y',
    figsize=(10, 6), include_legend=True
):
    """Plot the Prophet forecast.
    Parameters
    ----------
    m: Prophet model.
    fcst: pd.DataFrame output of m.predict.
    ax: Optional matplotlib axes on which to plot.
    uncertainty: Optional boolean to plot uncertainty intervals, which will
        only be done if m.uncertainty_samples > 0.
    plot_cap: Optional boolean indicating if the capacity should be shown
        in the figure, if available.
    xlabel: Optional label name on X-axis
    ylabel: Optional label name on Y-axis
    figsize: Optional tuple width, height in inches.
    include_legend: Optional boolean to add legend to the plot.
    Returns
    -------
    A matplotlib figure.
    """
    fig = plt.figure(facecolor='w', figsize=figsize)
    ax = fig.add_subplot(111)

    fcst['ds'] = pd.to_datetime(fcst['ds'], format='%Y-%m-%d')

    fcst_t = fcst['ds'].dt.to_pydatetime()
    ax.plot(fcst['ds'].dt.to_pydatetime(), fcst['y'], 'k.',
            label='Observed data points')
    ax.plot(fcst_t, fcst['yhat'], ls='-', c='#0072B2', label='Forecast')

    ax.fill_between(fcst_t, fcst['yhat_lower'], fcst['yhat_upper'],
                    color='#0072B2', alpha=0.2, label='Uncertainty interval')
    # Specify formatting to workaround matplotlib issue #12925
    locator = AutoDateLocator(interval_multiples=False)
    formatter = AutoDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.grid(True, which='major', c='gray', ls='-', lw=1, alpha=0.2)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    if include_legend:
        ax.legend()
    fig.tight_layout()
    return fig