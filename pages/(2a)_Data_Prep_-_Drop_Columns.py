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
st.write("### Data Preparation - Drop Columns")
dataset=pd.DataFrame()
col1,col2=st.columns([1,3], gap="medium")
with col1:
    sel_ds = st.selectbox("Select a dataset", options=datasets.keys())
    "---"
    if sel_ds:
        dataset=datasets[sel_ds]
        to_drop=st.multiselect("Select columns to drop:", sorted(dataset.columns))
        if st.button('Apply'):
            dataset=dataset.drop(columns=to_drop)
            datasets[sel_ds]=dataset
            st.session_state['datasets']=datasets
with col2:
    f"Records of {sel_ds}:"
    st.write(dataset.head())
    f"Statistics of {sel_ds}:"
    st.write(dataset.describe(include='all'))

