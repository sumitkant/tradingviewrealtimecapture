import pandas as pd
import numpy as np
import plotly.graph_objs as go
import plotly


def plot_pivot_markings(plot_df, START_DT, END_DT, LP_OFFSET, SP_OFFSET, BAR_OFFSET, ticker):

    # Plotting
    plot_df = plot_df[(pd.to_datetime(plot_df.date).dt.date >= pd.to_datetime(START_DT).date()) & (pd.to_datetime(plot_df.date).dt.date <= pd.to_datetime(END_DT).date())].reset_index(drop=True)
    plot_df.pivot_text.fillna('', inplace=True)
    y_plot_range = np.sqrt(plot_df.high.max() - plot_df.low.min())
    plot_df['y_plot_range'] = y_plot_range
    plot_df['large_pivot_y'] = (plot_df.high + plot_df.low)/2
    plot_df.loc[plot_df.LARGE_PIVOT == 'LPH', 'large_pivot_y'] = plot_df.high + y_plot_range*LP_OFFSET
    plot_df.loc[plot_df.LARGE_PIVOT == 'LPL', 'large_pivot_y'] = plot_df.low - y_plot_range*LP_OFFSET
    plot_df['pivot_y'] = (plot_df.high + plot_df.low)/2
    plot_df.loc[plot_df.pivot_text == 'SPH', 'pivot_y'] = plot_df.high + y_plot_range*SP_OFFSET
    plot_df.loc[plot_df.pivot_text == 'SPL', 'pivot_y'] = plot_df.low - y_plot_range*SP_OFFSET
    plot_df['broken_at_formatted'] = pd.to_datetime(plot_df['broken_at']).dt.strftime('%H:%M %m-%d-%Y')

    # dataframe for horizontal lines to mark first breaks of SPL and SPH
    LPH_indicator = plot_df[(plot_df.pivot_text.isin(['SPL','SPH'])) & (plot_df.break_order == 1) & (plot_df.broken == 1)]
    LPH_indicator = LPH_indicator[['datetime_formatted', 'broken_at_formatted', 'pivot_text', 'high', 'low']]
    LPH_indicator['y0'] = LPH_indicator.high
    LPH_indicator.loc[LPH_indicator.pivot_text == 'SPL', 'y0'] = LPH_indicator.low

    # Shapes to mark small pivot breaks
    large_pivot_breaks = []
    for i in LPH_indicator.index:
        large_pivot_breaks.append(
            dict(type="line", xref="x", yref="y",
                 x0=LPH_indicator.loc[i, 'datetime_formatted'],
                 y0=LPH_indicator.loc[i, 'y0'],
                 x1=LPH_indicator.loc[i, 'broken_at_formatted'],
                 y1=LPH_indicator.loc[i, 'y0'],
                 line=dict(color='rgb(0,0,0,0.2)', width=2, dash="dot")
                 )
        )

    # pivot hover text
    hover_text = []
    for i in range(plot_df.shape[0]):
        hover_text.append('<b style="font-size:16px">' + plot_df.pivot_text[i] + "</b><br>" +
                          '<b>' + str(plot_df['datetime_formatted'][i]) + '</b>' + "<br>" +
                          'O: ' + "%0.2f" % plot_df['open'][i] + "<br>" +
                          'H: ' + "%0.2f" % plot_df['high'][i] + "<br>" +
                          'L: ' + "%0.2f" % plot_df['low'][i] + "<br>" +
                          'C: ' + "%0.2f" % plot_df['close'][i] + "<br>" +
                          'V: ' + "%0.0f" % plot_df['volume'][i] + "<br>"
                          )

    # plot candlestick chart
    plot_data = [

        # Volumes
        go.Bar(
            x=plot_df['datetime_formatted'],
            y=plot_df.volume,
            marker_color='rgba(149, 165, 166, 0.5)',
            opacity=0.2,
            hoverinfo='skip',
            yaxis="y2"
        ),

        # OHLC PLOT
        go.Ohlc(
            x=plot_df['datetime_formatted'],
            open=plot_df['open'],
            high=plot_df['high'],
            low=plot_df['low'],
            close=plot_df['close'],
            text=hover_text,
            hoverinfo='text',
            increasing_line_color='rgb(16, 172, 132)',
            decreasing_line_color='rgb(240,57,100)',
            name='OHLC',
            line=dict(width=4)
        ),

        # SMALL PIVOT TEXT - SPH/SPL
        go.Scatter(
            x=plot_df['datetime_formatted'],
            y=plot_df.pivot_y,
            mode="text",
            name="Small Pivots",
            text=plot_df.pivot_text.values,
            textposition="middle center",
            textfont=dict(size=14, color='rgb(0,0,0,0.9)'),
            hoverinfo='skip'
        ),

        # SPL A12s
        go.Scatter(
            x=plot_df['datetime_formatted'],
            y=plot_df.low - y_plot_range*BAR_OFFSET,
            mode="text",
            name="SPL Bars",
            text=plot_df.SPL_bars.values,
            textposition="middle center",
            textfont=dict(size=12, color='rgba(0, 0, 0, 0.8)'),
            hoverinfo='skip',
        ),

        # SPH A12s
        go.Scatter(
            x=plot_df['datetime_formatted'],
            y=plot_df.high + y_plot_range*BAR_OFFSET,
            mode="text",
            name="SPH Bars",
            text=plot_df.SPH_bars.values,
            textposition="middle center",
            textfont=dict(size=12, color='rgba(0, 0, 0, 0.8)'),
            hoverinfo='skip'
        ),

        # LARGE PIVOTS
        go.Scatter(
            x=plot_df['datetime_formatted'],
            y=plot_df.large_pivot_y,
            mode="text",
            name="LARGE PIVOTS",
            text=plot_df.LARGE_PIVOT.fillna('').values,
            textposition="middle center",
            textfont=dict(size=18, color='rgb(240,57,100)'),
            hoverinfo='skip'
        ),


    ]

    fig = go.Figure(
        data=plot_data
    )
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=0, b=50, t=10, pad=0),
        width=1200,
        height=700,
        template='seaborn',
        paper_bgcolor='white',
        plot_bgcolor='white',
        hovermode="x",
        hoverlabel_align='right',
        shapes=large_pivot_breaks,
        yaxis=dict(
            gridcolor='rgba(178, 190, 195, 0)',
            nticks=10,
        ),
        yaxis2=dict(
            gridcolor='rgba(178, 190, 195, 0.2)',
            tickfont=dict(color='rgba(0,0,0,0)'),
            overlaying="y",
            side="right",

        ),
        showlegend=False
    )

    fig.update_xaxes(
        type='category',
        gridcolor='rgba(178, 190, 195, 0)',
        color='rgba(0,0,0,0.8)',
        tickangle=90
    )
    fig.update_yaxes(
        color='rgba(0,0,0,0.8)',
    )

    return fig
