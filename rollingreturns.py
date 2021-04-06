import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, date
from libs.streamlithelper import plot_indicators

def app():

    # inputs
    ticker = st.sidebar.text_input('Stock','ALKYLAMINE.NS')
    start_dt = st.sidebar.date_input('Start Date', date(2000, 1, 1))
    end_dt = st.sidebar.date_input('End Date (Today)', datetime.now().date())
    years = st.sidebar.slider('Years',1, 10, 1, 1)

    # computing returns
    window = 252 * years
    df = yf.download(ticker, start=start_dt, end=end_dt)
    
    adj_close = df[['Adj Close']]
    df['window_return'] = df['Adj Close'] / df['Adj Close'].shift(window) - 1
    df['max_roll'] = df['Adj Close'].rolling(window, min_periods=window).max()  
    df['daily_dd'] = df['Adj Close'] / df['max_roll'] - 1.0
    df['window_dd'] = df['daily_dd'].rolling(window, min_periods=1).min()
    df.dropna(inplace=True)
    st.write('Number of Data Points :', df.shape[0])

    y_axis_min = abs(df.window_dd.min())*1.10

    # stock plot return plot
    fig_stock = go.Figure()
    fig_stock.add_trace(go.Scatter(
        x=adj_close.index,
        y=adj_close['Adj Close'],
        name='Adjusted Close',
    ))
    fig_stock.update_layout(
        margin=dict(l=50, r=0, b=0, t=20, pad=0),
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=1200,
        height=400,
        yaxis=dict(zeroline=True),
    )

    # daily return plot
    fig_returns = go.Figure()
    fig_returns.add_trace(go.Scatter(
        x=df.index,
        y=df.window_return,
        name='Window Returns',
        line=dict(color='rgb(16, 172, 132)')
    ))
    fig_returns.update_layout(
        margin=dict(l=50, r=0, b=0, t=20, pad=0),
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=1200,
        height=400,
        yaxis=dict(zeroline=True),
    )

    # drawdown plot
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(
        x=df.index,
        y=df.window_dd,
        name='Window Drawdown',
        line=dict(color='rgb(240,57,100)'),

    ))
    fig_dd.add_trace(go.Scatter(
        x=df.index,
        y=df.daily_dd,
        name='Window Drawdown',
        line=dict(color='rgba(240,57,100, 0.4)'),

    ))
    fig_dd.update_layout(
        margin=dict(l=50, r=0, b=0, t=20, pad=0),
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=1200,
        height=400,
        yaxis=dict(zeroline=True, range=[-y_axis_min,0.01]),
        legend=dict(orientation='h',y=1.02, x=1,xanchor="right",yanchor="bottom",)
    )

    # # ------------------- Page Layout ------------------- #
    st.title(f'Rolling Returns for {ticker.split(".")[0]}')

    col1, col2, col3, col4 = st.beta_columns(4)

    # Daily return plot
    st.subheader(f'Adjusted Close')
    st.plotly_chart(fig_stock)

    # median returns
    median_return = round(df.window_return.quantile(0.5)*100, 2)
    fig_median_returns = plot_indicators(median_return, f'Median {years} year Return (%)', 300, 150)
    col1.plotly_chart(fig_median_returns)

    # Min Return
    min_return = round(df.window_return.min() * 100, 2)
    fig_min_returns = plot_indicators(min_return, f'Min {years} year Return (%)', 300, 150)
    col2.plotly_chart(fig_min_returns)

    # Avg Max drawdown
    avg_max_dd = round(df.window_dd.mean() * 100, 2)
    fig_avg_max_dd = plot_indicators(avg_max_dd, f'Average {years} year Max Drawdown (%)', 300, 150)
    col3.plotly_chart(fig_avg_max_dd)

    # Avg drawdown
    avg_dd = round(df.daily_dd.mean() * 100, 2)
    fig_avg_dd = plot_indicators(avg_dd, f'Average {years} year Drawdown (%)', 300, 150)
    col4.plotly_chart(fig_avg_dd)

    # Daily return plot
    st.subheader(f'{int(window / 252)} year rolling returns')
    st.plotly_chart(fig_returns)

    # Daily return plot
    st.subheader(f'{int(window / 252)} year max drawdowns')
    st.plotly_chart(fig_dd)
