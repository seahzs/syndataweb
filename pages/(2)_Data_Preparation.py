import streamlit as st
import pandas as pd

# Loads dataset from session state and updates sidebar
datasets={}
if 'datasets' not in st.session_state:
    st.error('Please load datasets to continue. *(See homepage)*')
else:
    datasets=st.session_state['datasets']
with st.sidebar:
    st.info('**Datasets loaded:**')
    for dataset in datasets:
        st.write(f"- {dataset}")

#Main Content
st.write("### Data Preparation")
