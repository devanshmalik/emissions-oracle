import os
import logging
import pandas as pd

import plotly.graph_objects as go
import plotly.io as pio

pio.templates.default = "simple_white"

log = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

# Formatting
COLORS = [
    '#1f77b4',  # muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf',  # blue-teal
]


def plot_prophet_forecast(fcst, title="", xlabel='Time', ylabel='y', figsize=(900, 600)):
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
    prediction_color = '#1f77b4'
    error_color = 'rgba(0, 114, 178, 0.2)'  # '#0072B2' with 0.2 opacity
    actual_color = 'black'
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
        title=title,
        width=figsize[0],
        height=figsize[1],
        yaxis=dict(
            title=ylabel
        ),
        xaxis=dict(
            title=xlabel,
            type='date',
            range=[pd.to_datetime('2001-03-31') - pd.DateOffset(months=6),
                   pd.to_datetime('2025-12-31') + pd.DateOffset(months=6)],
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


def plot_multiple_fuels(df, multiple_fuels, title="", xlabel='Time', ylabel='y', figsize=(900, 600)):
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
            line=dict(color=COLORS[idx], width=2),
        ))

        data.append(go.Scatter(
            name=fuel.title() + ' Forecast',
            x=df_forecast['date'],
            y=df_forecast[fuel],
            mode='lines',
            line=dict(color=COLORS[idx], width=2, dash='dot'),
        ))

    layout = dict(
        title=title,
        width=figsize[0],
        height=figsize[1],
        yaxis=dict(
            title=ylabel
        ),
        xaxis=dict(
            title=xlabel,
            type='date',
            range=[pd.to_datetime('2001-03-31') - pd.DateOffset(months=6),
                   pd.to_datetime('2025-12-31') + pd.DateOffset(months=6)],
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


def plot_multiple_states(fcst_by_states, filter_col,
                         title="", xlabel='Time', ylabel='y', figsize=(900, 600)):
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
            line=dict(color=COLORS[idx], width=2),
        ))

        data.append(go.Scatter(
            name=state + ' Forecast',
            x=df_forecast['date'],
            y=df_forecast[filter_col],
            mode='lines',
            line=dict(color=COLORS[idx], width=2, dash='dot'),
        ))

    layout = dict(
        title=title,
        width=figsize[0],
        height=figsize[1],
        yaxis=dict(
            title=ylabel
        ),
        xaxis=dict(
            title=xlabel,
            type='date',
            range=[pd.to_datetime('2001-03-31') - pd.DateOffset(months=6),
                   pd.to_datetime('2025-12-31') + pd.DateOffset(months=6)],
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
                                       xlabel='Time', ylabel='y', figsize=(900, 700)):
    curr_quarter_end = pd.to_datetime('today') - pd.tseries.offsets.QuarterEnd()
    data = []
    for idx, (state, df) in enumerate(emissions_by_states.items()):
        # Emissions Curves
        emissions_historical = df[df['date'] < curr_quarter_end]
        emissions_preds = df[df['date'] >= curr_quarter_end]

        data.append(go.Scatter(
            name="CO<sub>2</sub>eq - " + state,
            x=emissions_historical['date'],
            y=emissions_historical[fuel],
            mode='lines',
            line=dict(color=COLORS[idx], width=2),
        ))

        data.append(go.Scatter(
            name="CO<sub>2</sub>eq - " + state + ' Forecast',
            x=emissions_preds['date'],
            y=emissions_preds[fuel],
            mode='lines',
            line=dict(color=COLORS[idx], width=2, dash='dot'),
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
            line=dict(color=COLORS[idx], width=2),
            xaxis="x",
            yaxis="y2"
        ))

        data.append(go.Scatter(
            name=state + ' Forecast',
            x=gen_preds['date'],
            y=gen_preds[fuel],
            mode='lines',
            line=dict(color=COLORS[idx], width=2, dash='dot'),
            xaxis="x",
            yaxis="y2"
        ))

    layout = dict(
        width=figsize[0],
        height=figsize[1],
        yaxis=dict(
            title="Emissions (Thousand metric tons CO<sub>2</sub>eq)",
            domain=[0, 0.45]
        ),
        yaxis2=dict(
            title=ylabel,
            domain=[0.55, 1]
        ),
        xaxis1=dict(
            title=xlabel,
            type='date',
            range=[pd.to_datetime('2001-03-31') - pd.DateOffset(months=6),
                   pd.to_datetime('2025-12-31') + pd.DateOffset(months=6)],
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
                                      title="", xlabel='Time', ylabel='y', figsize=(900, 700)):
    data = []

    curr_quarter_end = pd.to_datetime('today') - pd.tseries.offsets.QuarterEnd()
    emissions_historical = df_emissions[df_emissions['date'] < curr_quarter_end]
    emissions_preds = df_emissions[df_emissions['date'] >= curr_quarter_end]
    # Append Emissions Curves
    for idx, fuel in enumerate(fuel_types):
        data.append(go.Scatter(
            name="CO<sub>2</sub>eq - " + fuel.title(),
            x=emissions_historical['date'],
            y=emissions_historical[fuel],
            mode='lines',
            line=dict(color=COLORS[idx], width=2),
        ))

        data.append(go.Scatter(
            name="CO<sub>2</sub>eq - " + fuel.title() + ' Forecast',
            x=emissions_preds['date'],
            y=emissions_preds[fuel],
            mode='lines',
            line=dict(color=COLORS[idx], width=2, dash='dot'),
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
            line=dict(color=COLORS[idx], width=2),
            xaxis="x",
            yaxis="y2"
        ))

        data.append(go.Scatter(
            name=fuel.title() + ' Forecast',
            x=gen_preds['date'],
            y=gen_preds[fuel],
            mode='lines',
            line=dict(color=COLORS[idx], width=2, dash='dot'),
            xaxis="x",
            yaxis="y2"
        ))

    layout = dict(
        title=title,
        width=figsize[0],
        height=figsize[1],
        yaxis=dict(
            title="Emissions (Thousand metric tons CO<sub>2</sub>eq)",
            domain=[0, 0.45]
        ),
        yaxis2=dict(
            title=ylabel,
            domain=[0.55, 1]
        ),
        xaxis1=dict(
            title=xlabel,
            type='date',
            range=[pd.to_datetime('2001-03-31') - pd.DateOffset(months=6),
                   pd.to_datetime('2025-12-31') + pd.DateOffset(months=6)],
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


def plot_map(df, filter_col, colorbar_title, title):
    fig = go.Figure(data=go.Choropleth(
        locations=df['state'],  # Spatial coordinates
        z=df[filter_col].astype(float),  # Data to be color-coded
        locationmode='USA-states',  # set of locations match entries in `locations`
        colorscale='YlOrRd',
        colorbar_title=colorbar_title,
    ))

    fig.update_layout(
        template="seaborn",
        width=900,
        height=600,
        title_text=title,
        geo_scope='usa',  # limited map scope to USA
    )

    return fig