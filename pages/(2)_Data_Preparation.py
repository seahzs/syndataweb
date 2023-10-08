import streamlit as st
import pandas as pd
st.set_page_config(layout='wide')

# Loads datasets from session state and updates sidebar
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
"### Data Preparation"
dataset=pd.DataFrame()
col1,col2,col3=st.columns([1,3,1])
with col1:
    task=st.selectbox("Task:", ("Drop Column(s)","Set Datatypes"))
    sel_ds = st.selectbox("Dataset:", options=datasets.keys())
    "---"
    if sel_ds:
        if task=="Drop Column(s)":
            dataset=datasets[sel_ds]
            to_drop=st.multiselect("Columns to drop:", sorted(dataset.columns))
            if st.button('Apply'):
                dataset=dataset.drop(columns=to_drop)
                datasets[sel_ds]=dataset
                st.session_state['datasets']=datasets
        elif task=="Set Datatypes":
            dataset=datasets[sel_ds]
            sel_cols=st.multiselect("Columns to convert:", sorted(dataset.columns))
            sel_dtype = st.selectbox("Datatype:", ('Int64','Float64','datetime64[ns]','boolean'))
            if st.button('Apply'):
                if sel_cols:
                    dataset[sel_cols]=dataset[sel_cols].astype(sel_dtype)
with col2:
    f"Records of {sel_ds}:"
    st.write(dataset.head(3))
    f"Statistics of {sel_ds}:"
    st.write(dataset.describe(include='all'))
with col3:
    f"Datatypes of {sel_ds}:"
    dataset.dtypes

