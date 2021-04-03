import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, date

def app():

    ticker = st.sidebar.text_input('Stock','ALKYLAMINE.NS')
    start_dt = st.sidebar.date_input('Start Date', date(2010, 1, 1))
    end_dt = st.sidebar.date_input('End Date', datetime.now().date())
    years = st.sidebar.slider('Years',1, 10, 1, 1)


    window = 252 * (years)
    df = yf.download(ticker, start=start_dt, end=end_dt)

    df['daily_return'] = df['Adj Close'].shift(-1) / df['Adj Close'] - 1
    df['window_return'] = df['Adj Close'].shift(-window) / df['Adj Close'] - 1
    # df['max_roll'] = df['Adj Close'].rolling(window, min_periods=window).max()
    # df['daily_dd'] = df['Adj Close'] / df['max_roll'] - 1.0
    # df['window_dd'] = df['daily_dd'].rolling(window, min_periods=window).min()
    df.dropna(inplace=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df.window_return,
        name='Window Returns'
    ))
    # fig.add_trace(go.Scatter(
    #     x=df.index,
    #     y=df.window_dd,
    #     name='Window Drawdowns'
    # ))
    fig.update_layout(margin=dict(l=50, r=0, b=150, t=20, pad=0),
                      width=1200,
                      height=600,
                      xaxis_title='Year',
                      yaxis_title='Return',
                      )
    st.title(f'Rolling Returns for {ticker.split(".")[0]}')

    # st.subheader(f'Mean Return {int(window / 252)} year period')
    # st.header(f'{round(df.window_return.mean()*100, 2)} %')

    st.subheader(f'Median Return {int(window / 252)} year period')
    st.header(f'{round(df.window_return.quantile(0.5)*100, 2)} %')

    st.subheader(f'Min Return {int(window / 252)} year period')
    st.header(f'{round(df.window_return.min()*100, 2)} %')

    st.subheader(f'{int(window / 252)} year retuns and max {int(window / 252)} year drawdown')
    st.plotly_chart(fig)
