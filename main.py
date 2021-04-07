import streamlit as st
import pivot_markings_backtest
import rollingreturns
import portfolioevaluate
from libs.streamlithelper import show_logo

# Custom CSS
st.markdown("""
<style>
.reportview-container .main .block-container{max-width: 80%;}
</style>
""", unsafe_allow_html=True,)

PAGES = {
    "Realtime Pivot Marking": pivot_markings_backtest,
    "Stock Rolling Returns": rollingreturns,
    'Portfolio Evaluation': portfolioevaluate,
}

c1, c2, c3 = st.beta_columns((3, 1, 3))
c2.image(show_logo(), width=150)
st.markdown('---')
st.subheader('Tools')
selection = st.radio("", list(PAGES.keys()))
st.markdown('---')
# Logo
page = PAGES[selection]
page.app()

# headings
