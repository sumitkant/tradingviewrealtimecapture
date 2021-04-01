import streamlit as st
import pandas as pd
import json

df = pd.read_csv('messages.txt', sep='\n', header=None)
for i in range(df.shape[0]):
    item = [x for x in df.loc[i,0].split('~') if x]
    # st.write(item)
    for k in item:
        try:
            st.write(json.loads(k))
        except:
            pass