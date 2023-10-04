import streamlit as st
import pandas as pd

# Loads dataset from session state and updates sidebar
datasets={}
if 'datasets' not in st.session_state:
    st.error('Please load datasets to continue.')
else:
    datasets=st.session_state['datasets']
with st.sidebar:
    '**Datasets loaded:**'
    for dataset in datasets:
        st.info(f"- {dataset}")


#prepare data
st.write("### Data Preparation - Set Datatypes")
sel_ds = st.selectbox("Select a dataset", options=datasets.keys())
"---"
if sel_ds:
    dataset=datasets[sel_ds]
    to_convert={}
    "Select columns to convert:"
    col1, col2 = st.columns(2)
    with col1:
        for dtype in ('Int64','Float64',):
            to_convert[dtype]=st.multiselect(f"'{dtype}':", sorted(dataset.columns))
    with col2:
        for dtype in ('datetime64[ns]','boolean'):
            to_convert[dtype]=st.multiselect(f"'{dtype}':", sorted(dataset.columns))
    if st.button('Apply'):
        for dtype, sel_cols in to_convert.items():
            if sel_cols:
                dataset[sel_cols]=dataset[sel_cols].astype(dtype)
        "---"
        f"Datatypes of '{sel_ds}':"
        dataset.dtypes

