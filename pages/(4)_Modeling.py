import streamlit as st
import pandas as pd
import numpy as np
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.single_table import CTGANSynthesizer
from sdv.single_table import CopulaGANSynthesizer
from sdv.metadata import SingleTableMetadata

st.set_page_config(layout='wide')

# Loads datasets from session state and updates sidebar
datasets={}
models={}
if 'datasets' not in st.session_state:
    st.error('Please load datasets to continue.')
else:
    datasets=st.session_state['datasets']
with st.sidebar:
    '**Datasets loaded:**'
    for dataset in datasets:
        st.info(f"- {dataset}")

#Main Content
st.write("### Modeling")
col1,col2=st.columns([1,3],gap="medium")
with col1:
    sel_ds = st.selectbox("Dataset:", options=datasets.keys())
    if sel_ds:
        dataset=datasets[sel_ds]
        metadata = SingleTableMetadata()
        metadata.detect_from_dataframe(dataset)
        with st.expander("Show metadata:"):
            st.write(pd.DataFrame.from_dict(metadata.columns).transpose())
        sel_key = st.selectbox("Primary Key:", options=dataset.columns)
        sel_ML=st.selectbox("Synthesizer:", options=("Gaussian Copula","CTGAN","Copula GAN"))
        sel_epochs=st.slider('Epochs:', 1, 300)
        if st.button("Fit dataset"):
            metadata.update_column(column_name=sel_key,sdtype='id')
            metadata.set_primary_key(column_name=sel_key)
            if sel_ML=="Gaussian Copula":
                synthesizer = GaussianCopulaSynthesizer(metadata)
            elif sel_ML=="CTGAN":
                synthesizer = CTGANSynthesizer(metadata, epochs=sel_epochs)
            elif sel_ML=="Copula GAN":
                synthesizer = CopulaGANSynthesizer(metadata, epochs=sel_epochs)
            with col2:
                with st.spinner('Fitting data, please wait...'):
                    synthesizer.fit(dataset)
                "Generated Sample:"
                st.write(synthesizer.sample(num_rows=10))
