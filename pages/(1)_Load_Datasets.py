import streamlit as st
import pandas as pd

# Loads dataset from session state and updates sidebar
datasets={}
if 'datasets' not in st.session_state:
    st.error('Please load datasets to continue. *(See homepage)*')
else:
    datasets=st.session_state['datasets']
with st.sidebar:
    st.info('**Datasets loaded:**')
    for dataset in datasets:
        st.write(f"- {dataset}")

# Main Content
st.write("### Load Datasets")
files = st.file_uploader("Upload dataset CSV file(s):", type="csv", accept_multiple_files=True)
if files:
    for csv_file in files:
        dataset=csv_file.name.split('.')[0]
        datasets[dataset] = pd.read_csv(csv_file)
        st.session_state["datasets"]=datasets
        with st.expander(f"**{dataset}** - {datasets[dataset].shape}"):
            st.write(datasets[dataset].head(3))
        with st.sidebar:
            st.write(f"- {dataset}")