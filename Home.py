import streamlit as st
import pandas as pd
from sdv.metadata import SingleTableMetadata
st.set_page_config(page_title='Synthetic Data Web App',layout='wide')

# Loads datasets and models from session state and updates sidebar
datasets=st.session_state['datasets'] if 'datasets' in st.session_state else {}
single_metadata=st.session_state['single_metadata'] if 'single_metadata' in st.session_state else {}
multi_metadata=st.session_state['multi_metadata'] if 'multi_metadata' in st.session_state else {}
models=st.session_state['models'] if 'models' in st.session_state else {}
syn_datasets=st.session_state['syn_datasets'] if 'syn_datasets' in st.session_state else {}
with st.sidebar:
    with st.expander("Datasets"):
        for dataset in datasets:
            f"- {dataset}"
    with st.expander("Grouped Datasets"):
        if multi_metadata:
            for dataset in multi_metadata['datasets']:
                f"- {dataset}"
    with st.expander("Fitted Models - Single Table"):
        for dataset_models in models:
            f"{dataset_models}:"
            for model in models[dataset_models]:
                f"- {model}"
    with st.expander("Generated Data - Single Table"):
        for syn_dataset in syn_datasets:
            f"{syn_dataset}:"
            for model_gen in syn_datasets[syn_dataset]:
                f"- {model_gen}"

# Guide
"### Generation and Analysis of Synthetic Data"
"**Workflow:** *Load Data > Prepare > Model > Generate > Visualise > Export*"
"---"
col1,col2=st.columns([2,5], gap="medium")
with col1:
    st.error("To begin, please upload datasets first.")
    "**Step 1:** Upload CSV files"
    files = st.file_uploader("Upload dataset CSV file(s):", type="csv", accept_multiple_files=True, label_visibility="collapsed")
    if files:
        "---"
        "**Step 2:** Load datasets *(tables)* from CSV files"
        headers = st.checkbox("CSV files has headers", value=True)
        skip_rows = st.text_input("Number of rows to Skip:", placeholder="Enter an integer")
        if st.button("Load dataset(s)"):
            with col2:
                "**Step 3:** Verify headers and records"
                for csv_file in files:
                    dataset=csv_file.name.split('.')[0]
                    datasets[dataset] = pd.read_csv(csv_file, skiprows=int(skip_rows) if skip_rows else 0, header='infer' if headers else None)
                    metadata=SingleTableMetadata()
                    metadata.detect_from_dataframe(data=datasets[dataset])
                    single_metadata[dataset]=metadata
                    st.session_state["datasets"]=datasets
                    st.session_state["single_metadata"]=single_metadata
                    f"**{dataset}** - Preview (*{datasets[dataset].shape[1]}* columns, *{datasets[dataset].shape[0]}* records)"
                    st.write(datasets[dataset].head(3))
                st.success("If headers are incorrect, repeat step 2, otherwise proceed to **'(2) Data 'Preparation'**.")