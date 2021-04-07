import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, date
from libs.streamlithelper import plot_indicators

@st.cache
def get_data(stocks, start_dt, end_dt):
    data = yf.download(stocks, start=start_dt, end=end_dt)['Adj Close']
    return data

def compute_rolling_returns(indexed, years):
    window = 252 * years
    indexed['portfolio'] = indexed.sum(axis=1)
    indexed['portfolio'] = indexed.portfolio*100 / indexed.portfolio.iloc[0]
    indexed['window_return'] = indexed['portfolio'] / indexed['portfolio'].shift(window) - 1
    indexed['max_roll'] = indexed['portfolio'].rolling(window, min_periods=window).max()
    indexed['daily_dd'] = indexed['portfolio'] / indexed['max_roll'] - 1.0
    indexed['window_dd'] = indexed['daily_dd'].rolling(window, min_periods=1).min()
    # indexed.dropna(inplace=True)
    return indexed


def app():

    # inputs
    start_dt = st.sidebar.date_input('Start Date', date(2010, 1, 1))
    end_dt = st.sidebar.date_input('End Date (Today)', datetime.now().date())
    benchmark = st.sidebar.text_input('Benchmark', '^NSEI')
    years = st.sidebar.slider('Years', 1, 10, 1, 1)
    tickers = st.text_input('Stocks', 'ALKYLAMINE.NS, BAJFINANCE.NS')
    quantities = st.text_input('Quantity', '1,2')

    # Header
    st.title("Evaluate Portfolio!")
    st.write(f'Number of Stocks : {len(tickers.split(","))}')


    tickers = [x.strip() for x in tickers.split(',')]
    quantities = [int(x.strip()) for x in quantities.split(',')]
    portfolio_data = get_data(tickers, start_dt, end_dt)
    benchmark_data = get_data(benchmark, start_dt, end_dt)

    if len(tickers) == 1:
        values = [portfolio_data.iloc[-1] for x in tickers]
    else:
        values = [portfolio_data[x].iloc[-1] for x in tickers]


    st.header('Portfolio table')
    port_table = pd.DataFrame({
        'Stocks':tickers,
        'Price': values,
        'Qty': quantities,
    }).set_index('Stocks')
    port_table['Value'] = port_table.Price * port_table.Qty
    port_table['Weight'] = port_table['Value']/port_table.Value.sum()
    st.table(port_table)

    st.header(f'Investment Amount : {round(port_table.Value.sum(),2)}')

    indexed = portfolio_data*100/portfolio_data.iloc[0]
    if len(tickers) == 1:
        indexed = indexed * quantities
        indexed = indexed.to_frame()
    else:
        for ticker, qty in zip(tickers,quantities):
            indexed[ticker] = indexed[ticker]*qty


    benchmark_indexed = benchmark_data*100*sum(quantities)/benchmark_data.iloc[0]

    # computing returns
    portfolio_returns = compute_rolling_returns(indexed, years)
    benchmark_returns = compute_rolling_returns(benchmark_indexed.to_frame(), years)

    # st.write(benchmark_returns.head())

    # st.write(returns.head())

    st.subheader(f'Portfolio vs {benchmark} - Indexed Returns')
    # stock plot return plot
    fig_stock = go.Figure()
    fig_stock.add_trace(go.Scatter(
        x=benchmark_returns.index,
        y=benchmark_returns.portfolio,
        name=benchmark,
    ))
    fig_stock.add_trace(go.Scatter(
        x=portfolio_returns.index,
        y=portfolio_returns.portfolio,
        name='Portfolio',
    ))
    fig_stock.update_layout(
        margin=dict(l=50, r=20, b=20, t=20, pad=0),
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=1200,
        height=500,
        yaxis=dict(zeroline=True),
        legend=dict(orientation='h', y=1.02, x=1, xanchor="right", yanchor="bottom", )
    )
    st.plotly_chart(fig_stock)

    st.title(f'Rolling Returns for Portfolio')

    col1, col2 = st.beta_columns(2)
    col1.subheader('Benchmark')
    col2.subheader('Portfolio')


    # # Daily return plot
    # st.subheader(f'Adjusted Close')
    # st.plotly_chart(fig_stock)
    #
    # median returns
    median_return = round(benchmark_returns.window_return.quantile(0.5) * 100, 2)
    fig_median_returns = plot_indicators(median_return, f'Median {years} year Return (%)', 300, 150)
    col1.plotly_chart(fig_median_returns)

    # median returns
    median_return = round(portfolio_returns.window_return.quantile(0.5) * 100, 2)
    fig_median_returns = plot_indicators(median_return, f'Median {years} year Return (%)', 300, 150)
    col2.plotly_chart(fig_median_returns)


    # Min Return
    min_return = round(benchmark_returns.window_return.min() * 100, 2)
    fig_min_returns = plot_indicators(min_return, f'Min {years} year Return (%)', 300, 150)
    col1.plotly_chart(fig_min_returns)

    min_return = round(portfolio_returns.window_return.min() * 100, 2)
    fig_min_returns = plot_indicators(min_return, f'Min {years} year Return (%)', 300, 150)
    col2.plotly_chart(fig_min_returns)


    # Avg Max drawdown
    avg_max_dd = round(benchmark_returns.window_dd.mean() * 100, 2)
    fig_avg_max_dd = plot_indicators(avg_max_dd, f'Average {years} year Max Drawdown (%)', 300, 150)
    col1.plotly_chart(fig_avg_max_dd)

    avg_max_dd = round(portfolio_returns.window_dd.mean() * 100, 2)
    fig_avg_max_dd = plot_indicators(avg_max_dd, f'Average {years} year Max Drawdown (%)', 300, 150)
    col2.plotly_chart(fig_avg_max_dd)

    # Avg drawdown
    avg_dd = round(benchmark_returns.daily_dd.mean() * 100, 2)
    fig_avg_dd = plot_indicators(avg_dd, f'Average {years} year Drawdown (%)', 300, 150)
    col1.plotly_chart(fig_avg_dd)

    # Avg drawdown
    avg_dd = round(portfolio_returns.daily_dd.mean() * 100, 2)
    fig_avg_dd = plot_indicators(avg_dd, f'Average {years} year Drawdown (%)', 300, 150)
    col2.plotly_chart(fig_avg_dd)

    # daily return plot
    fig_returns = go.Figure()
    fig_returns.add_trace(go.Scatter(
        x=benchmark_returns.dropna().index,
        y=benchmark_returns.dropna().window_return,
        name='Benchmark Returns',
    ))
    fig_returns.add_trace(go.Scatter(
        x=portfolio_returns.dropna().index,
        y=portfolio_returns.dropna().window_return,
        name='Portfolio Returns',
    ))
    fig_returns.update_layout(
        margin=dict(l=50, r=0, b=0, t=20, pad=0),
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=1200,
        height=400,
        yaxis=dict(zeroline=True),
        legend=dict(orientation='h', y=1.02, x=1, xanchor="right", yanchor="bottom", )
    )

    # Daily return plot
    st.subheader(f'{int(years)} year rolling returns')
    st.plotly_chart(fig_returns)

    # drawdown plot
    fig_dd = go.Figure()
    fig_dd.add_trace(go.Scatter(
        x=benchmark_returns.dropna().index,
        y=benchmark_returns.dropna().daily_dd,
        name='Benchmark Drawdown',
        opacity=0.5

    ))
    fig_dd.add_trace(go.Scatter(
        x=portfolio_returns.dropna().index,
        y=portfolio_returns.dropna().daily_dd,
        name='Portfolio Drawdown',
        opacity=0.5

    ))
    y_axis_min = abs(benchmark_returns.window_dd.min())
    y_axis_min_p = abs(portfolio_returns.window_dd.min())
    y_min = max(y_axis_min, y_axis_min_p)*1.10
    fig_dd.update_layout(
        margin=dict(l=50, r=0, b=0, t=20, pad=0),
        template='plotly_white',
        paper_bgcolor='white',
        plot_bgcolor='white',
        width=1200,
        height=400,
        yaxis=dict(zeroline=True, range=[-y_min, 0.01]),
        legend=dict(orientation='h', y=1.02, x=1, xanchor="right", yanchor="bottom", )
    )

    # Daily return plot
    st.subheader(f'{int(years)} year drawdowns')
    st.plotly_chart(fig_dd)

