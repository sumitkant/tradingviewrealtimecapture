import streamlit as st
from datetime import datetime, timedelta
from libs.structuralpivotmarkings import mark_all_pivots
from libs.plotter import plot_pivot_markings
from libs.tvfetch import search_data
from libs.resampler import resample_data
from libs.streamlithelper import get_table_download_link, show_logo
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

def app():
    # headings
    st.title('Realtime Pivot Marking')
    st.subheader('Streaming Realtime data from tradingview')
    st.markdown("""
    * Fetches OHLC data from TradingView in Realtime (all tickers supported by TradingView - max 5000 candles)
    * Cleans and resamples data when required
    * **Auto-refreshes every 30 seconds** and marks small and large pivot marking 
    * Plots the markings on the resmapled dataframe
    ---
    ### Dataset Options
    """)

    c1, c2 = st.columns((3, 3))

    # Sidebar Options

    ticker = c1.text_input('Symbol (TradingView)', 'NSE:NIFTY1!')
    resolution = c2.selectbox('Resolution Interval (MIN)', ("1", "3", "5", "10", "15", "30", "60", "120", "240", "D", "W"), 2)
    bars = c1.slider('Number of Bars',  10, 5000, 288, 10)
    #refresh_freq = c2.slider('Refresh Frequency (SEC)', 10, 600, 60, 10)
    resample = c2.selectbox('Resample Resolution (MIN)', ("1", "3", "5", "10", "15", "30", "60", "120", "240"), 5)

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

    # start_date = datetime.now().strftime('%Y-%m-%d 09:15:00')
    # end_date = datetime.now().strftime('%Y-%m-%d 15:30:00')
    # st.write(start_date, end_date)
    # date_ranges = pd.date_range(start=start_date, end=end_date, closed=None, freq='1min')
    # time_list = [x.strftime('%Y-%m-%d %H:%M:%S') for x in date_ranges]
    # st.write(time_list)
    #
    # while True:
    #     if datetime.now().strftime('%Y-%m-%d %H:%M:%S') in time_list:
    #         st.write('TimePassed :', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    #         sleep(30)
    #
    #
    #
    # Update Button

    def mark_pivot_now():
        # get data from trading view
        st.subheader(f'{ticker} Chart')
        data = search_data(ticker, resolution, bars)
        st.markdown(get_table_download_link(data, f'Download {bars} rows of {resolution}min timeframe (CSV)'), unsafe_allow_html=True)
        st.write('Refreshed at :', datetime.now())

        # check if needs resampling
        if resample != resolution:
            data_resampled = resample_data(data, resample, resolution)
        else:
            data_resampled = data

        # Small and large pivot marking on resampled data
        data_marked = mark_all_pivots(data_resampled, 'datetime')

        # st.write('Last Small Pivot :',
        #          data_marked[data_marked.pivot_text.isin(['SPH', 'SPL'])].tail(1).pivot_text.values[0],
        #          'formed at :',
        #          pd.to_datetime(data_marked[data_marked.pivot_text.isin(['SPH','SPL'])].tail(1).SP_FORMED_AT.values[0]))
        # st.write('Last Large Pivot :',
        #          data_marked[data_marked.LARGE_PIVOT.isin(['LPH', 'LPL'])].tail(1).LARGE_PIVOT.values[0],
        #          'formed at :',
        #          pd.to_datetime((data_marked[data_marked.pivot_text.isin(['SPH','SPL']) & (data_marked.break_order == 1)].tail(1).broken_at.values[0])))
        # st.write('Last SPH :',
        #          data_marked[data_marked.pivot_text.isin(['SPH'])].tail(1).high.values[0],
        #          'formed at :',
        #          pd.to_datetime(data_marked[data_marked.pivot_text.isin(['SPH'])].tail(1).SP_FORMED_AT.values[0]))
        # st.write('Last SPL :',
        #          data_marked[data_marked.pivot_text.isin(['SPL'])].tail(1).low.values[0],
        #          'formed at :',
        #          pd.to_datetime(data_marked[data_marked.pivot_text.isin(['SPL'])].tail(1).SP_FORMED_AT.values[0]))
        # st.write('Last LPH',
        #          data_marked[data_marked.LARGE_PIVOT.isin(['LPH'])].tail(1).high.values[0],
        #          'by breaking SPL at :',
        #          pd.to_datetime(data_marked[(data_marked.pivot_text.isin(['SPL'])) & (data_marked.break_order == 1)].tail(1).broken_at.values[0]))
        # st.write('Last LPL',
        #          data_marked[data_marked.LARGE_PIVOT.isin(['LPL'])].tail(1).low.values[0],
        #          'by breaking SPH at :',
        #          pd.to_datetime(data_marked[(data_marked.pivot_text.isin(['SPH'])) & (data_marked.break_order == 1)].tail(1).broken_at.values[0]))


        st.markdown(get_table_download_link(data_marked, f'Download marked data @ {resample}min timeframe (CSV)'),
                    unsafe_allow_html=True)


        print(data_marked.head())
        # plotting data

        figure = plot_pivot_markings(data_marked, START_DT, END_DT, LP_OFFSET, SP_OFFSET, BAR_OFFSET, ticker)
        return figure

    # Auto-refresh
    st_autorefresh(interval=30 * 1000, key="dataframerefresh")
    st.plotly_chart(mark_pivot_now(), use_container_width=True)

