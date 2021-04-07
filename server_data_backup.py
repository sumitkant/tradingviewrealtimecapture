# import streamlit as st
# from datetime import datetime, timedelta
# from libs.structuralpivotmarkings import mark_all_pivots
# from libs.plotter import plot_pivot_markings
# from libs.tvfetch import fetch_raw_data
# from libs.resampler import resample_data
# from libs.streamlithelper import get_table_download_link, show_logo
# import pandas as pd
# from datetime import datetime
# from time import sleep
# import gspread
# import pygsheets
# from oauth2client.service_account import ServiceAccountCredentials
#
#
# tickers = ['NSE:NIFTY1!', 'NSE:NIFTY2!','NSE:BANKNIFTY1!', 'NSE:BANKNIFTY2!']
# resolution = 1
# bars = 5000
#
# def backup_data():
#     for ticker in tickers:
#         data = fetch_raw_data(ticker, resolution, bars)
#         data['date'] = pd.to_datetime(data.datetime).dt.date
#         data = data[data.date == datetime.now().date]
#         print(data)
#         data
#
