import streamlit as st
from websocket import create_connection
from tvstreamhelper import generateSession, generateChartSession, sendMessage, generate_csv
import json
import base64
import re
import pandas as pd
from time import sleep
from datetime import datetime, timedelta
import plotly.graph_objs as go
import plotly

# Initialize the headers needed for the websocket connection
headers = json.dumps({'Origin': 'https://data.tradingview.com'})

# Then create a connection to the tunnel
def newSession():
    ws = create_connection(
        'wss://data.tradingview.com/socket.io/websocket',headers=headers)

    session = generateSession()
    chart_session = generateChartSession()
    return ws, session, chart_session

def messagebox(ws, session, chart_session, ticker, resolution, bars):
    sendMessage(ws, "set_auth_token", ["unauthorized_user_token"])
    sendMessage(ws, "chart_create_session", [chart_session, ""])
    sendMessage(ws, "quote_create_session", [session])
    sendMessage(ws, "quote_set_fields", [session,"ch","chp","current_session","description","local_description","language","exchange","fractional","is_tradable","lp","lp_time","minmov","minmove2","original_name","pricescale","pro_name","short_name","type","update_mode","volume","currency_code","rchp","rtc"])
    sendMessage(ws, "quote_add_symbols", [session, ticker, {"flags": ['force_permission']}])
    sendMessage(ws, "quote_fast_symbols", [session, ticker])
    sendMessage(ws, "resolve_symbol", [chart_session,"symbol_1","={\"symbol\":\"NSE:NIFTY1!\",\"adjustment\":\"splits\",\"session\":\"extended\"}"])
    sendMessage(ws, "create_series", [chart_session, "s1", "s1", "symbol_1", resolution, bars])

def search_data():
    ws, session, chart_session = newSession()
    messagebox(ws, session, chart_session, ticker, resolution, bars)

    search_tu = True
    while search_tu:
        try:
            result = ws.recv()
            result = result.split('~')

            for item in result:
                if 'timescale_update' in item:
                    item = pd.DataFrame([x['v'] for x in json.loads(item)['p'][1]['s1']['s']])
                    item.columns = ['datetime','open','high','low','close','volume']
                    item['datetime_fmt'] = pd.to_datetime(item.datetime, unit='s') + timedelta(hours=5.5)
                    item = item.head(bars)
                    return item
                    search_tu = False

        except Exception as e:
            item = ''
            return item
            st.write(e)
            break

# pivot hover text
def plot_data(df, ticker):
    hover_text = []
    for i in range(df.shape[0]):
        hover_text.append('<b>' + str(df['datetime_fmt'][i]) + '</b>' + "<br>" +
                          'O: ' + "%0.2f" % df['open'][i] + "<br>" +
                          'H: ' + "%0.2f" % df['high'][i] + "<br>" +
                          'L: ' + "%0.2f" % df['low'][i] + "<br>" +
                          'C: ' + "%0.2f" % df['close'][i] + "<br>")

    ohlc_plot = go.Ohlc(
            x=df['datetime_fmt'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            text=hover_text,
            hoverinfo='text',
            increasing_line_color='rgb(46, 204, 113)',
            decreasing_line_color='rgb(231, 76, 60)',
            name='OHLC')

    plot_data = [ohlc_plot]

    fig = go.Figure(data=plot_data)
    fig.update_layout(xaxis_rangeslider_visible=False,
                      margin=dict(l=50, r=0, b=150, t=100, pad=0),
                      height=600,
                      template='plotly_dark',
                      title=ticker,
                      paper_bgcolor='black',
                      plot_bgcolor='black',
                      hovermode="x",
                      hoverlabel_align='right'
                      )
    fig.update_xaxes(type='category', gridcolor='rgba(255, 255, 255, 0.1)', color='rgb(127, 140, 141)')
    fig.update_yaxes(gridcolor='rgba(255, 255, 255, 0.1)', color='rgb(127, 140, 141)')
    return fig

def resample_data(df, resample, resolution):
    if resolution != resample:
        aggregations = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum'}
        resampled_df = df.resample(
            rule=resample + 'Min',   # timeframe
            on='datetime_fmt',            # Resampling column
            origin='2010-01-04 9:15:00',  # starting point of resampling
            closed='left',               # considers data at 9:45 1min candle
            label='left',                 # chooses datetime label of at the end of time period eg. 9:15 to 9:45 would use 9:15 for left and 9:45 for right
        ).agg(aggregations).dropna()
        resampled_df = resampled_df.reset_index()
        return resampled_df

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
    return href


# ------------------------ Page Layout ------------------------ #

# headings
st.title('Trading View Realtime')
st.subheader('Streaming Realtime data from tradingview')

# Sidebar Options
st.sidebar.header('Options')
ticker = st.sidebar.text_input('Symbol (TradingView)', 'NSE:NIFTY1!')
resolution = st.sidebar.selectbox('Resolution (Interval)', ("1", "3", "5", "10", "15", "30", "60", "120", "240", "D", "W"), 0)
bars = st.sidebar.slider('Number of Bars',  10, 10000, 360, 10)
resample = st.sidebar.selectbox('Resample Resolution', ("1", "3", "5", "10", "15", "30", "60", "120", "240"), 5)

# Update Button
if st.button('Refresh Data'):
    ohlc = search_data()
    if resample != resolution:
        ohlc_resampled = resample_data(ohlc, resample, resolution)
    else:
        ohlc_resampled = ohlc
    # st.subheader('Data fetched from TradingView')
    st.table(ohlc.head())
    st.markdown(get_table_download_link(ohlc), unsafe_allow_html=True)
    # st.markdown('---')
    # st.write('Refreshed at :', datetime.now())
    # st.subheader('Resampled Data')
    # st.table(ohlc_resampled)
    st.markdown('---')
    # st.subheader('Chart')
    figure = plot_data(ohlc_resampled, ticker)
    st.plotly_chart(figure)





