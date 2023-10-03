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


# Load datasets
st.write("### Load Datasets")
files = st.file_uploader("Upload dataset CSV file(s):", type="csv", accept_multiple_files=True)
headers = st.checkbox("CSV files has headers", value=True)
skip_rows = st.text_input("Number of rows to Skip:", placeholder="Enter an integer")
if files:
    for csv_file in files:
        dataset=csv_file.name.split('.')[0]
        datasets[dataset] = pd.read_csv(csv_file, skiprows=int(skip_rows) if skip_rows else 0, header='infer' if headers else None)
        st.session_state["datasets"]=datasets
        with st.expander(f"**{dataset}** - {datasets[dataset].shape}"):
            st.write(datasets[dataset].head(3))
        with st.sidebar:
            st.info(f"- {dataset}")
    st.success("To continue, go to **'(2) Data 'Preparation'** on the sidebar.")