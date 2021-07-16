import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import numpy as np
import time

def open_browser():
    # Opens Chrome Browser
    path_to_chromedriver = 'assets/chromedriver.exe'
    brow = webdriver.Chrome(executable_path=path_to_chromedriver)
    return brow

st.title('Economic Times Scrape')

#
# browser = open_browser()
# ihtml = pd.DataFrame()
# for i in range(1, 21):
#     URL = f'https://economictimes.indiatimes.com/marketstats/pageno-{i},pid-61,sortby-currentYearRank,sortorder-asc,year-2020.cms'
#     browser.get(URL)
#     time.sleep(2)
#     companyobj = browser.find_elements_by_xpath("//div[@class='dataList']")
#     ihtml = ihtml.append(pd.DataFrame({
#         'page': [i],
#         'innerHTML': [[x.get_attribute('innerHTML') for x in companyobj]]
#     }), ignore_index=True)
#     st.write(f'Done for page {i}')
# ihtml.to_pickle('assets/et500scraped.pkl')
# browser.close()
#
# df = pd.read_pickle('assets/et500scraped.pkl')
# innerHTML = []
# for i in range(df.shape[0]):
#     for x in df.innerHTML.values[i]:
#         innerHTML.append(x)
# # st.write(innerHTML)
# etURLS = pd.DataFrame()
# for h in innerHTML:
#     soup = BeautifulSoup(h, 'html.parser').find('a')
#     etURLS = etURLS.append(pd.DataFrame({
#         'title': [soup.text],
#         'url': [soup['href']],
#         'seoName': [soup['href'].split('/')[1]],
#         'companyid':[soup['href'].split('-')[-1].split('.')[0]]
#     }), ignore_index=True)
# st.table(etURLS.drop_duplicates())
# etURLS.to_csv('assets/et500urls.csv', index=False)
