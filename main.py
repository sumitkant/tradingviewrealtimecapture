import streamlit as st
from datetime import datetime, timedelta
from libs.structuralpivotmarkings import mark_all_pivots
from libs.plotter import plot_pivot_markings
from libs.tvfetch import search_data
from libs.resampler import resample_data
from libs.streamlithelper import get_table_download_link

# Custom CSS
st.markdown(
"""
<style>
.reportview-container .main .block-container{max-width: 80%;}
</style>
""",
unsafe_allow_html=True,
)

# headings
st.title('Realtime Pivot Markings')
st.subheader('Streaming Realtime data from tradingview')
st.markdown("""
* Fetches OHLC data from TradingView in Realtime (all tickers supported by TradingView - max 5000 candles)
* Cleans and resamples data when required
* Marks small and large pivots
* Plots the markings on the resmapled dataframe
---
""")


# Sidebar Options
st.sidebar.header('Dataset Options')
ticker = st.sidebar.text_input('Symbol (TradingView)', 'NSE:NIFTY1!')
resolution = st.sidebar.selectbox('Resolution (Interval)', ("1", "3", "5", "10", "15", "30", "60", "120", "240", "D", "W"), 2)
bars = st.sidebar.slider('Number of Bars',  10, 5000, 288, 10)
resample = st.sidebar.selectbox('Resample Resolution', ("1", "3", "5", "10", "15", "30", "60", "120", "240"), 5)

st.sidebar.header('Charting Options')
default_start = (datetime.now() - timedelta(days=365)).date()
default_end = (datetime.now()).date()
START_DT = default_start
END_DT = default_end

# START_DT = st.sidebar.date_input('Start Date', default_start)
# END_DT = st.sidebar.date_input('End Date', default_end)
LP_OFFSET = st.sidebar.slider('Large Pivot Label Offset', 0.0, 5.0, 2.25, 0.25)
SP_OFFSET = st.sidebar.slider('Small Pivot Label Offset', 0.0, 5.0, 1.25, 0.25)
BAR_OFFSET = st.sidebar.slider('Small Pivot Bar offset', 0.0, 5.0, 0.5, 0.25)




# Update Button
if st.sidebar.button('Refresh Data'):

    # get data from trading view
    data = search_data(ticker, resolution, bars)
    st.markdown(get_table_download_link(data, f'Download {bars} rows of {resolution} timeframe (CSV)'), unsafe_allow_html=True)
    st.write('Refreshed at :', datetime.now())

    # check if needs resampling
    if resample != resolution:
        data_resampled = resample_data(data, resample, resolution)
    else:
        data_resampled = data

    # Small and large pivot marking on resampled data    
    data_marked = mark_all_pivots(data_resampled, 'datetime')

    # plotting data
    st.subheader(f'{ticker} Chart')
    figure = plot_pivot_markings(data_marked, START_DT, END_DT, LP_OFFSET, SP_OFFSET, BAR_OFFSET, ticker)
    st.plotly_chart(figure)
