import streamlit as st
from apps import pivot_markings_backtest, rollingreturns
from libs.streamlithelper import show_logo

# Custom CSS
st.markdown("""
<style>
.reportview-container .main .block-container{max-width: 80%;}
</style>
""", unsafe_allow_html=True,)



PAGES = {
    "Realtime Pivot Marking": pivot_markings_backtest,
    "Stock Rolling Returns": rollingreturns
}
st.image(show_logo(), width=70)
st.subheader('Page Navigator')
selection = st.radio("", list(PAGES.keys()))
st.markdown('---')
# Logo

page = PAGES[selection]
page.app()

# headings
