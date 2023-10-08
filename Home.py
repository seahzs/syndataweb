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

# Guide
"## Generation and Analysis of Synthetic Data"
"**Tasks Outline:**"
"1) Load datasets from CSV files"
"2) Prepare datasets - drop columns, set datatypes)"
"3) Dataset visualisation - distribution, correlation"
"4) ML modeling - metadata, fitting"
"5) Generate synthetic datasets"
"6) Synthetic data visualisation"
"7) Export synthetic data to CSV file"