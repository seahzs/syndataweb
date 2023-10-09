import streamlit as st
import pandas as pd
import numpy as np
from sdv.single_table import GaussianCopulaSynthesizer
from sdv.single_table import CTGANSynthesizer
from sdv.single_table import CopulaGANSynthesizer
from sdv.metadata import SingleTableMetadata
st.set_page_config(page_title='Synthetic Data Web App',layout='wide')

# Loads datasets and models from session state and updates sidebar
with st.spinner("Loading from cache, please wait..."):
    datasets=st.session_state['datasets'] if 'datasets' in st.session_state else {}
    models=st.session_state['models'] if 'models' in st.session_state else {}
    syn_datasets=st.session_state['syn_datasets'] if 'syn_datasets' in st.session_state else {}
    with st.sidebar:
        with st.expander("Datasets"):
            for dataset in datasets:
                f"- {dataset}"
        with st.expander("Fitted Models"):
            for dataset_models in models:
                f"{dataset_models}:"
                for model in models[dataset_models]:
                    f"- {model}"
        with st.expander("Synthetic Data"):
            for syn_dataset in syn_datasets:
                f"{syn_dataset}:"
                for model_gen in syn_datasets[syn_dataset]:
                    f"- {model_gen}"

#Main Content
"### Modeling"
st.error('Please load datasets to continue.') if datasets=={} else ""
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
        sel_ml=st.selectbox("Synthesizer:", options=("Gaussian Copula","CTGAN","Copula GAN"))
        sel_epochs=st.slider('Epochs:', 1, 300)
        if st.button("Fit dataset"):
            metadata.update_column(column_name=sel_key,sdtype='id')
            metadata.set_primary_key(column_name=sel_key)
            if sel_ml=="Gaussian Copula":
                synthesizer = GaussianCopulaSynthesizer(metadata)
            elif sel_ml=="CTGAN":
                synthesizer = CTGANSynthesizer(metadata, epochs=sel_epochs)
            elif sel_ml=="Copula GAN":
                synthesizer = CopulaGANSynthesizer(metadata, epochs=sel_epochs)
            with col2:
                with st.spinner('Fitting data, please wait...'):
                    synthesizer.fit(dataset)
                if sel_ds not in models.keys():
                    models[sel_ds]={}
                models[sel_ds][sel_ml]=synthesizer
                st.session_state['models']=models
                "Generated Sample:"
                st.write(synthesizer.sample(num_rows=10))
