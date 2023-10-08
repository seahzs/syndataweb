import streamlit as st
import pandas as pd
st.set_page_config(layout='wide')

# Loads datasets and models from session state and updates sidebar
datasets={}
models={}
if 'datasets' not in st.session_state:
    st.error('Please load datasets to continue.')
else:
    datasets=st.session_state['datasets']
if 'models' in st.session_state:
    models=st.session_state['models']
with st.sidebar:
    with st.expander("Datasets"):
        for dataset in datasets:
            f"- {dataset}"
    with st.expander("Models"):
        for dataset_models in models:
            f"{dataset_models}:"
            for model in models[dataset_models]:
                f"- {model}"

#prepare data
"### Data Preparation"
dataset=pd.DataFrame()
col1,col2,col3=st.columns([1,3,1])
with col1:
    sel_ds = st.selectbox("Dataset:", options=datasets.keys())
    sel_task=st.selectbox("Task:", ("Drop Column(s)","Set Datatypes"))
    "---"
    if sel_ds:
        if sel_task=="Drop Column(s)":
            dataset=datasets[sel_ds]
            to_drop=st.multiselect("Columns to drop:", sorted(dataset.columns))
            if st.button('Apply'):
                dataset=dataset.drop(columns=to_drop)
                datasets[sel_ds]=dataset
                st.session_state['datasets']=datasets
        elif sel_task=="Set Datatypes":
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

