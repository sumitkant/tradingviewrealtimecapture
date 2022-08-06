import streamlit as st
import pivot_markings_backtest
import rollingreturns
import portfolioevaluate
import moneycontrolNewsScrape
import weeklyStockSuggestor
from libs.streamlithelper import show_logo

# # Custom CSS
# st.markdown("""
# <style>
# .reportview-container .main .block-container{max-width: 80%;}
# </style>
# """, unsafe_allow_html=True,)
st.set_page_config(layout="wide")


PAGES = {
    "Realtime Pivot Marking": pivot_markings_backtest,
    "Stock Rolling Returns": rollingreturns,
    'Portfolio Evaluation': portfolioevaluate,
    'News Listings' : moneycontrolNewsScrape,
    'Weekly Stock Suggestion' :  weeklyStockSuggestor
}

c1, c2, c3 = st.columns((3, 1, 3))
c2.image(show_logo(), width=150)
st.sidebar.subheader('Tools')
selection = st.sidebar.selectbox("", list(PAGES.keys()))
st.markdown('---')
# Logo
page = PAGES[selection]
page.app()

# headings
