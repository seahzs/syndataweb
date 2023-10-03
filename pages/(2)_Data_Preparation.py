import streamlit as st
import pandas as pd

# Loads dataset and updates dataset list in sidebar
datasets = {}
with st.sidebar:
    for dataset_name in ('Survey 2020', 'Survey 2021', 'Survey 2022'):
        if dataset_name in st.session_state:
            datasets[dataset_name]=st.session_state[dataset_name]
    st.write('**Loaded Datasets:**')
    st.info(", ".join(datasets.keys()))

#Main Content
st.write("### Data Preparation")
st.write("Please select the preparation task(s) to be performed.")
fix_headers = st.checkbox('**Rename Features** - *for column matching*')
filter_common = st.checkbox('**Filter Common Features** - *drop columns not found across multiple datasets*')
merge_headers = st.checkbox('**Combine Features** - *merge related columns into one feature*')
if st.button('Submit'):
    pass