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
st.write("### Data Preparation")

"(A) Set Column Data Types"
sel_ds = st.selectbox("Select a dataset", options=datasets.keys())
if sel_ds:
    dataset=datasets[sel_ds]
    col1, col2 = st.columns([1,3])
    with col1:
        dataset.dtypes
    with col2:
        # if st.button('Auto-detect datatypes'):
        #     dataset.convert_dtypes()
        # "---"
        to_convert={}
        for dtype in ('datetime64[ns]','Int64','Float64','string','boolean'):
            to_convert[dtype]=st.multiselect(f"Select column(s) to convert to '{dtype}':", sorted(dataset.columns))
        if st.button('Apply'):
            for dtype, sel_cols in to_convert.items():
                dataset[sel_cols].astype(dtype)

