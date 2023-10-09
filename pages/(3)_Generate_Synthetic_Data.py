import streamlit as st
import pandas as pd
import numpy as np
st.set_page_config(page_title='Synthetic Data Web App',layout='wide')

with st.spinner("Loading ML libraries, please wait..."):
    from sdv.single_table import GaussianCopulaSynthesizer
    from sdv.single_table import CTGANSynthesizer
    from sdv.single_table import CopulaGANSynthesizer
    from sdv.metadata import SingleTableMetadata

# Loads datasets and models from session state and updates sidebar
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
"### Generate Synthetic Data"
if datasets=={} or models=={}:
    st.error('Please load & fit datasets to continue.')
else:
    col1,col2=st.columns([1,3],gap="medium")
    with col1:
        sel_ds = st.selectbox("Dataset:", options=models.keys())
        if sel_ds:
            dataset_models=models[sel_ds]
            sel_ml = st.selectbox("Fitted Model:", options=dataset_models.keys())
            n=datasets[sel_ds].shape[0]
            sel_n = st.number_input(f"Records to generate (real data has {n}):", value=n, format="%i", min_value=0, step=n)
            if st.button("Generate"):
                with col2:
                    with st.spinner('Generating data, please wait...'):
                        syn_data=dataset_models[sel_ml].sample(num_rows=sel_n)
                    if sel_ds not in syn_datasets.keys():
                        syn_datasets[sel_ds]={}
                    syn_datasets[sel_ds][sel_ml]=syn_data
                    st.session_state['syn_datasets']=syn_datasets
                    f"Records of generated '{sel_ds}' using {sel_ml}:"
                    st.write(syn_data.head())
                    f"Statistics of generated '{sel_ds}' using {sel_ml}:"
                    st.write(syn_data.describe(include='all'))
            
