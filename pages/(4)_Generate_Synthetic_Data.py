import streamlit as st
import pandas as pd
import numpy as np
from sdv import Metadata
from sdv.single_table import CTGANSynthesizer
from sdv.single_table import GaussianCopulaSynthesizer
#from sdgym.synthesizers import TableGAN

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

#Main Content
st.write("### Generate Synthetic Data")
col1,col2=st.columns([1,4],gap="medium")
with col1:
    sel_ds = st.selectbox("Select a dataset", options=datasets.keys())
    "---"
    if sel_ds:
        dataset=datasets[sel_ds]