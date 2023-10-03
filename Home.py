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


# Guide
st.write("## Generation and Analysis of Synthetic Data")
"**Guidelines:**"
"- **Step 1:** Load dataset(s) from CSV file(s)."
"- **Step 2:** Prepare datasets. (clean, drop, impute, etc.)"
"- **Step 3:** Preliminary visualisation and analysis."
"- **Step 4:** Generate synthetic data."
"- **Step 5:** Preliminary visualisation and analysis."