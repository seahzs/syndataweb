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

# Load datasets
"### Load Datasets"
col1,col2=st.columns([2,5], gap="medium")
with col1:
    "**Step 1:** Upload CSV file(s)"
    files = st.file_uploader("Upload dataset CSV file(s):", type="csv", accept_multiple_files=True, label_visibility="collapsed")
    if files:
        "---"
        "**Step 2:** Load dataset(s) from CSV files"
        headers = st.checkbox("CSV files has headers", value=True)
        skip_rows = st.text_input("Number of rows to Skip:", placeholder="Enter an integer")
        if st.button("Load dataset(s)"):
            with col2:
                "**Step 3:** Verify headers and records"
                for csv_file in files:
                    dataset=csv_file.name.split('.')[0]
                    datasets[dataset] = pd.read_csv(csv_file, skiprows=int(skip_rows) if skip_rows else 0, header='infer' if headers else None)
                    st.session_state["datasets"]=datasets
                    f"**{dataset}** - {datasets[dataset].shape}"
                    st.write(datasets[dataset].head())
                st.success("If headers are incorrect, repeat step 2, otherwise proceed to **'(2) Data 'Preparation'**.")