# streamlit run dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import requests
import base64


# Sidebar
option = st.sidebar.selectbox('Which Dashboard?', (
    'Streamlit Features',
    'Money Control Price Feed'))

st.title(option)

if option == 'Streamlit Features':

    # Displaying Simple Text

    st.header('This is a header')
    st.subheader('Subheading for the header')
    st.write('Turn data scripts into sharable web apps in minutes. All in Python. All for free. No front-end experience required.')

    # Automatically Renders Markdown

    """
    # Markdown Title
    ## Markdown Header
    ### Markdown Subheader
    Markdown Text rendered automatically using streamlit magic
    
    ---
    """

    # Dictionary
    st.subheader('Auto renders dictionaries')
    {'a': 0, 'b':1}

    #list
    st.subheader('Auto renders list')
    list = [1, 2, 3]
    st.write(list)

    # pandas dataframe


    df = pd.DataFrame(range(10), np.random.randn(10))
    st.dataframe(df)

if option == 'Money Control Price Feed':

    def get_table_download_link(df):
        """Generates a link allowing the data in a given panda dataframe to be downloaded
        in:  dataframe
        out: href string
        """
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
        href = f'<a href="data:file/csv;base64,{b64}">Download csv file</a>'
        return href


    """
    ---
    """
    symbol = st.text_input('Ticker Symbol', 'BAJFINANCE')
    start_time = st.date_input('Start Date', (datetime.now() - timedelta(days=30)))
    end_time = st.date_input('End Date', datetime.now())
    resolution = st.select_slider('Resolution', (1, 3, 5, 15, 30, 60, '1d'))
    """
    ---
    """


    st.subheader('Feed Data')
    st.write('Displaying last 20 rows')
    URL = 'https://priceapi.moneycontrol.com/techCharts/techChartController/history?symbol={}&resolution={}&from={}&to={}'.format(
        symbol, resolution, int(pd.to_datetime(start_time).timestamp()), int(pd.to_datetime(end_time).timestamp()))
    # st.write(URL)
    response = requests.get(URL)
    if response.status_code == requests.codes.ok:
        df = pd.DataFrame(response.json())
        df.drop('s', axis=1, inplace=True)
        df.columns = ['time', 'open', 'high',    'low', 'close', 'volume']
        df['datetime'] = pd.to_datetime(df['time'], unit='s') + timedelta(hours=5.5)
        st.dataframe(df.tail(20))
        st.markdown(get_table_download_link(df), unsafe_allow_html=True)
