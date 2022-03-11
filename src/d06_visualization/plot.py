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
from plotly.subplots import make_subplots

import plotly.graph_objects as go

from pandas.plotting import deregister_matplotlib_converters
deregister_matplotlib_converters()

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

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
    '#17becf'  # blue-teal
]

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


def plot_prophet_forecast(fcst, xlabel='ds', ylabel='y', figsize=(900, 600)):
    """Plot the Prophet forecast with actual and prediction values.
    The plot shows the uncertainty ranges for each prediction.

    Parameters
    ----------
    fcst:
        pd.DataFrame output of Prophet model
    xlabel:
        Optional label name on X-axis
    ylabel:
        Optional label name on Y-axis

    Returns
    -------
    A Plotly Figure.
    """
    # Formatting
    prediction_color = '#0072B2'
    error_color = 'rgba(0, 114, 178, 0.2)'  # '#0072B2' with 0.2 opacity
    actual_color = 'black'
    trend_color = '#B23B00'
    line_width = 2
    marker_size = 4

    fcst_historical = fcst[fcst['ds'] < pd.to_datetime('today')]
    data = []
    # Add actual
    data.append(go.Scatter(
        name='Actual',
        x=fcst_historical['ds'],
        y=fcst_historical['y'],
        marker=dict(color=actual_color, size=marker_size),
        mode='markers'
    ))
    # Add uncertainty lower bound
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
        fill='tonexty'
    ))
    # Add uncertainty upper bound
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


def plot_multiple_fuels(df, multiple_fuels, xlabel='ds', ylabel='y', figsize=(900, 600)):
    curr_quarter_end = pd.to_datetime('today') - pd.tseries.offsets.QuarterEnd()
    df_historical = df[df['date'] < curr_quarter_end]
    df_forecast = df[df['date'] >= curr_quarter_end]

    data = []
    for idx, fuel in enumerate(multiple_fuels):
        data.append(go.Scatter(
            name=fuel.title(),
            x=df_historical['date'],
            y=df_historical[fuel],
            mode='lines',
            line=dict(color=colors[idx], width=2),
        ))

        data.append(go.Scatter(
            name=fuel.title() + ' Forecast',
            x=df_forecast['date'],
            y=df_forecast[fuel],
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
            range=[df['date'].min() - pd.DateOffset(months=6),
                   df['date'].max() + pd.DateOffset(months=6)],
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


def plot_multiple_states(fcst_by_states, filter_col, xlabel='ds', ylabel='y', figsize=(900, 600)):
    data = []
    curr_quarter_end = pd.to_datetime('today') - pd.tseries.offsets.QuarterEnd()
    for idx, (state, df) in enumerate(fcst_by_states.items()):
        df_historical = df[df['date'] < curr_quarter_end]
        df_forecast = df[df['date'] >= curr_quarter_end]

        data.append(go.Scatter(
            name=state,
            x=df_historical['date'],
            y=df_historical[filter_col],
            mode='lines',
            line=dict(color=colors[idx], width=2),
        ))

        data.append(go.Scatter(
            name=state + ' Forecast',
            x=df_forecast['date'],
            y=df_forecast[filter_col],
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
            range=[df['date'].min() - pd.DateOffset(months=6),
                   df['date'].max() + pd.DateOffset(months=6)],
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


def plot_combined_data_multiple_states(gen_by_states, emissions_by_states, fuel,
                                       xlabel='ds', ylabel='y', figsize=(900, 700)):
    curr_quarter_end = pd.to_datetime('today') - pd.tseries.offsets.QuarterEnd()
    data = []
    for idx, (state, df) in enumerate(emissions_by_states.items()):
        # Emissions Curves
        emissions_historical = df[df['date'] < curr_quarter_end]
        emissions_preds = df[df['date'] >= curr_quarter_end]

        data.append(go.Scatter(
            name="CO<sub>2</sub>e - " + state,
            x=emissions_historical['date'],
            y=emissions_historical[fuel],
            mode='lines',
            line=dict(color=colors[idx], width=2),
        ))

        data.append(go.Scatter(
            name="CO<sub>2</sub>e - " + state + ' Forecast',
            x=emissions_preds['date'],
            y=emissions_preds[fuel],
            mode='lines',
            line=dict(color=colors[idx], width=2, dash='dot'),
        ))

        # Electricity Generation Curves
        df = gen_by_states[state]
        gen_historical = df[df['date'] < curr_quarter_end]
        gen_preds = df[df['date'] >= curr_quarter_end]

        data.append(go.Scatter(
            name=state,
            x=gen_historical['date'],
            y=gen_historical[fuel],
            mode='lines',
            line=dict(color=colors[idx], width=2),
            xaxis="x",
            yaxis="y2"
        ))

        data.append(go.Scatter(
            name=state + ' Forecast',
            x=gen_preds['date'],
            y=gen_preds[fuel],
            mode='lines',
            line=dict(color=colors[idx], width=2, dash='dot'),
            xaxis="x",
            yaxis="y2"
        ))

    layout = dict(
        width=figsize[0],
        height=figsize[1],
        yaxis=dict(
            # title=ylabel,
            domain=[0, 0.45]
        ),
        yaxis2=dict(
            domain=[0.55, 1]
        ),
        xaxis1=dict(
            type='date',
            range=[df['date'].min() - pd.DateOffset(months=6),
                   df['date'].max() + pd.DateOffset(months=6)],
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
        ),
        xaxis2=dict(
            anchor="y2",
        ),
    )
    return go.Figure(data=data, layout=layout)


def plot_combined_data_multiple_fuels(df_generation, df_emissions, fuel_types,
                                      xlabel='ds', ylabel='y', figsize=(900, 700)):
    data = []

    curr_quarter_end = pd.to_datetime('today') - pd.tseries.offsets.QuarterEnd()
    emissions_historical = df_emissions[df_emissions['date'] < curr_quarter_end]
    emissions_preds = df_emissions[df_emissions['date'] >= curr_quarter_end]
    # Append Emissions Curves
    for idx, fuel in enumerate(fuel_types):
        data.append(go.Scatter(
            name="CO<sub>2</sub>e - " + fuel.title(),
            x=emissions_historical['date'],
            y=emissions_historical[fuel],
            mode='lines',
            line=dict(color=colors[idx], width=2),
        ))

        data.append(go.Scatter(
            name="CO<sub>2</sub>e - " + fuel.title() + ' Forecast',
            x=emissions_preds['date'],
            y=emissions_preds[fuel],
            mode='lines',
            line=dict(color=colors[idx], width=2, dash='dot'),
        ))

    # Generation Curves
    gen_historical = df_generation[df_generation['date'] < curr_quarter_end]
    gen_preds = df_generation[df_generation['date'] >= curr_quarter_end]
    for idx, fuel in enumerate(fuel_types):
        data.append(go.Scatter(
            name=fuel.title(),
            x=gen_historical['date'],
            y=gen_historical[fuel],
            mode='lines',
            line=dict(color=colors[idx], width=2),
            xaxis="x",
            yaxis="y2"
        ))

        data.append(go.Scatter(
            name=fuel.title() + ' Forecast',
            x=gen_preds['date'],
            y=gen_preds[fuel],
            mode='lines',
            line=dict(color=colors[idx], width=2, dash='dot'),
            xaxis="x",
            yaxis="y2"
        ))

    layout = dict(
        width=figsize[0],
        height=figsize[1],
        yaxis=dict(
            # title=ylabel,
            domain=[0, 0.45]
        ),
        yaxis2=dict(
            domain=[0.55, 1]
        ),
        xaxis1=dict(
            type='date',
            # TODO clean this area up
            range=[df_generation['date'].min() - pd.DateOffset(months=6),
                   df_generation['date'].max() + pd.DateOffset(months=6)],
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
        ),
        xaxis2=dict(
            anchor="y2",
        ),
    )
    return go.Figure(data=data, layout=layout)


def plot_map(df, filter_col):
    fig = go.Figure(data=go.Choropleth(
        locations=df['state'],  # Spatial coordinates
        z=df[filter_col].astype(float),  # Data to be color-coded
        locationmode='USA-states',  # set of locations match entries in `locations`
        colorscale='Reds',
        colorbar_title="Thousand Metric Tons CO2e",
    ))

    fig.update_layout(
        width=900,
        height=600,
        title_text='US Total Electricity Generation Emissions by State',
        geo_scope='usa',  # limited map scope to USA
    )

    return fig