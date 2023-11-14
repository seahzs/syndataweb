import streamlit as st
st.set_page_config(page_title='Synthetic Data Web App',layout='wide')
import pandas as pd
from sdv.metadata import SingleTableMetadata

# Loads datasets and models from session state and updates sidebar
datasets=st.session_state['datasets'] if 'datasets' in st.session_state else {}
single_metadata=st.session_state['single_metadata'] if 'single_metadata' in st.session_state else {}
multi_metadata=st.session_state['multi_metadata'] if 'multi_metadata' in st.session_state else {}
single_models=st.session_state['single_models'] if 'single_models' in st.session_state else {}
multi_models=st.session_state['multi_models'] if 'multi_models' in st.session_state else {}
single_synthetic=st.session_state['single_synthetic'] if 'single_synthetic' in st.session_state else {}
multi_synthetic=st.session_state['multi_synthetic'] if 'multi_synthetic' in st.session_state else {}
with st.sidebar:
    "***Need help?***  *See [documentation](https://github.com/seahzs/syndataweb/) on Github.*"
    with st.expander("Tables"):
        for dataset in datasets:
            f"- {dataset}"
    with st.expander("Grouped Tables"):
        if multi_metadata:
            for dataset in multi_metadata['datasets']:
                f"- {dataset}"
    with st.expander("Fitted Single Tables"):
        for dataset_models in single_models:
            f"{dataset_models}:"
            for model in single_models[dataset_models]:
                f"- {model}"
    with st.expander("Fitted Multiple Tables"):
        for model in multi_models:
            f"- {model}"
    with st.expander("Generated Single Table"):
        for syn_dataset in single_synthetic:
            f"{syn_dataset}:"
            for model in single_synthetic[syn_dataset]:
                f"- {model}"
    with st.expander("Generated Multiple Tables"):
        for model in multi_synthetic:
            f"{model}"
            for dataset in multi_synthetic[model]:
                f"- {dataset}"
# Main Content
"### Synthetic Data Web App"
"**Workflow:** *Load Data > Prepare > Model > Generate > Visualise > Export*"
st.info("To begin, please upload tables first. Ensure that data is well-prepared with headers and no missing values.")
"### Upload data"
col1,col2=st.columns([2,5])
with col1:
    files = st.file_uploader("Select CSV files:", type="csv", accept_multiple_files=True)
    "---"
    if files:
        headers = st.checkbox("CSV files has headers", value=True)
        skip_rows = st.text_input("Number of rows to Skip:", placeholder="Enter an integer")
        if st.button("Load CSV files"):
            st.info("**Hint:** If headers appears to be incorrect, adjust the parameters above and reload CSV files.")
            with col2:
                with st.spinner("Loading CSV files..."):
                    f"{len(files)} tables loaded:"
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