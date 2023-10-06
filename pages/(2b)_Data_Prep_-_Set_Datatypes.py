import streamlit as st
import pandas as pd
st.set_page_config(layout='wide')

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
dataset=pd.DataFrame()
col1,col2=st.columns([1,3], gap="medium")
with col1:
    sel_ds = st.selectbox("Select dataset", options=datasets.keys())
    "---"
    if sel_ds:
        dataset=datasets[sel_ds]
        sel_cols=st.multiselect("Select columns to convert:", sorted(dataset.columns))
        sel_dtype = st.selectbox("Select dtype:", ('Int64','Float64','datetime64[ns]','boolean'))
        if st.button('Apply'):
            if sel_cols:
                dataset[sel_cols]=dataset[sel_cols].astype(sel_dtype)
with col2:
    f"Statistics of {sel_ds}:"
    st.write(dataset.describe(include='all'))
    f"Datatypes of {sel_ds}:"
    dataset.dtypes
