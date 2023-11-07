import streamlit as st
import pandas as pd
st.set_page_config(page_title='Synthetic Data Web App',layout='wide')

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
"### Export Synthetic Data"
if datasets=={} or models=={}:
    st.error('Please load & fit datasets with modeling.')
else:
    col1,col2=st.columns([1,3],gap="medium")
    with col1:
        sel_ds = st.selectbox("Synthetic Dataset:", options=syn_datasets.keys())
        if sel_ds:
            sel_ml = st.selectbox("Fitted Model:", options=syn_datasets[sel_ds].keys())
            syn_dataset=syn_datasets[sel_ds][sel_ml]
        st.download_button("Download as CSV file",syn_dataset.to_csv(index=False).encode('utf-8'),f"{sel_ds}_syn.csv","text/csv",key='download-csv')
        with col2:
            f"Records of synthetic '{sel_ds}' generated using '{sel_ml}':"
            st.write(syn_dataset.head(3))
            f"Statistics of synthetic '{sel_ds}' generated using '{sel_ml}':"
            st.write(syn_dataset.describe(include='all'))