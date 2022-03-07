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
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots

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


def plot_plotly_individual(fcst, uncertainty=True, trend=False,
                           xlabel='ds', ylabel='y', figsize=(900, 600)):
    """Plot the Prophet forecast with Plotly offline.
    Plotting in Jupyter Notebook requires initializing plotly.offline.init_notebook_mode():
    >>> import plotly.offline as py
    >>> py.init_notebook_mode()
    Then the figure can be displayed using plotly.offline.iplot(...):
    >>> fig = plot_plotly(m, fcst)
    >>> py.iplot(fig)
    see https://plot.ly/python/offline/ for details
    Parameters
    ----------
    m: Prophet model.
    fcst: pd.DataFrame output of m.predict.
    uncertainty: Optional boolean to plot uncertainty intervals.
    plot_cap: Optional boolean indicating if the capacity should be shown
        in the figure, if available.
    trend: Optional boolean to plot trend
    changepoints: Optional boolean to plot changepoints
    changepoints_threshold: Threshold on trend change magnitude for significance.
    xlabel: Optional label name on X-axis
    ylabel: Optional label name on Y-axis
    Returns
    -------
    A Plotly Figure.
    """
    fcst['ds'] = pd.to_datetime(fcst['ds'], format='%Y-%m-%d')
    fcst_historical = fcst[fcst['ds'] < pd.to_datetime('today')]

    # Formatting
    prediction_color = '#0072B2'
    error_color = 'rgba(0, 114, 178, 0.2)'  # '#0072B2' with 0.2 opacity
    actual_color = 'black'
    trend_color = '#B23B00'
    line_width = 2
    marker_size = 4

    data = []
    # Add actual
    data.append(go.Scatter(
        name='Actual',
        x=fcst_historical['ds'],
        y=fcst_historical['y'],
        marker=dict(color=actual_color, size=marker_size),
        mode='markers'
    ))
    # Add lower bound
    if uncertainty:
        data.append(go.Scatter(
            x=fcst['ds'],
            y=fcst['yhat_lower'],
            mode='lines',
            line=dict(width=0),
            hoverinfo='skip',
            showlegend=False,
        ))
    # Add prediction
    data.append(go.Scatter(
        name='Predicted',
        x=fcst['ds'],
        y=fcst['yhat'],
        mode='lines',
        line=dict(color=prediction_color, width=line_width),
        fillcolor=error_color,
        fill='tonexty' if uncertainty else 'none'
    ))
    # Add upper bound
    if uncertainty:
        data.append(go.Scatter(
            x=fcst['ds'],
            y=fcst['yhat_upper'],
            mode='lines',
            line=dict(width=0),
            fillcolor=error_color,
            fill='tonexty',
            hoverinfo='skip',
            showlegend=False,
        ))

    # Add trend
    if trend:
        data.append(go.Scatter(
            name='Trend',
            x=fcst['ds'],
            y=fcst['trend'],
            mode='lines',
            line=dict(color=trend_color, width=line_width),
        ))

    layout = dict(
        width=figsize[0],
        height=figsize[1],
        yaxis=dict(
            title=ylabel
        ),
        xaxis=dict(
            title=xlabel,
            type='date',
            range=[fcst['ds'].min() - pd.DateOffset(months=6),
                   fcst['ds'].max() + pd.DateOffset(months=6)],
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1y',
                         step='year',
                         stepmode='backward'),
                    dict(count=3,
                         label='3y',
                         step='year',
                         stepmode='backward'),
                    dict(count=5,
                         label='5y',
                         step='year',
                         stepmode='backward'),
                    dict(count=10,
                         label='10y',
                         step='year',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
        ),
    )
    fig = go.Figure(data=data, layout=layout)
    return fig


def plot_plotly_combined(fcst, fuel_types,
                           xlabel='ds', ylabel='y', figsize=(900, 600)):
    curr_quarter_end = pd.to_datetime('today') - pd.tseries.offsets.QuarterEnd()
    fcst['date'] = pd.to_datetime(fcst['date'], format='%Y-%m-%d')
    fcst_historical = fcst[fcst['date'] < curr_quarter_end]
    fcst_preds = fcst[fcst['date'] >= curr_quarter_end]

    # Formatting
    colors = [
        '#1f77b4',  # muted blue
        '#ff7f0e',  # safety orange
        '#2ca02c',  # cooked asparagus green
        '#d62728',  # brick red
        '#9467bd',  # muted purple
        '#8c564b',  # chestnut brown
        '#e377c2',  # raspberry yogurt pink
        '#7f7f7f',  # middle gray
        '#bcbd22',  # curry yellow-green
        '#17becf'   # blue-teal
    ]

    data = []
    for idx, fuel in enumerate(fuel_types):
        data.append(go.Scatter(
            name=fuel.title(),
            x=fcst_historical['date'],
            y=fcst_historical[fuel],
            # mode='lines+markers',
            mode='lines',
            line=dict(color=colors[idx], width=2),
        ))

        data.append(go.Scatter(
            name=fuel.title() + ' Forecast',
            x=fcst_preds['date'],
            y=fcst_preds[fuel],
            # mode='lines+markers',
            mode='lines',
            line=dict(color=colors[idx], width=2, dash='dot'),
        ))

    layout = dict(
        width=figsize[0],
        height=figsize[1],
        yaxis=dict(
            title=ylabel
        ),
        xaxis=dict(
            title=xlabel,
            type='date',
            range=[fcst['date'].min() - pd.DateOffset(months=6),
                   fcst['date'].max() + pd.DateOffset(months=6)],
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1y',
                         step='year',
                         stepmode='backward'),
                    dict(count=3,
                         label='3y',
                         step='year',
                         stepmode='backward'),
                    dict(count=5,
                         label='5y',
                         step='year',
                         stepmode='backward'),
                    dict(count=10,
                         label='10y',
                         step='year',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
        ),
    )
    return go.Figure(data=data, layout=layout)