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
"### Data Preparation"
if datasets=={}:
    st.error('Please load datasets to continue.')
else:
    col1,col2,col3=st.columns([1,3,1])
    with col1:
        sel_ds = st.selectbox("Dataset:", options=datasets.keys())
        sel_task=st.selectbox("Task:", ("Set Datatypes","Drop Column(s)"))
        "---"
        if sel_ds:
            if sel_task=="Drop Column(s)":
                dataset=datasets[sel_ds]
                to_drop=st.multiselect("Columns to drop:", sorted(dataset.columns))
                if st.button('Apply'):
                    dataset=dataset.drop(columns=to_drop)
                    datasets[sel_ds]=dataset
                    st.session_state['datasets']=datasets
            elif sel_task=="Set Datatypes":
                dataset=datasets[sel_ds]
                sel_cols=st.multiselect("Columns to convert:", sorted(dataset.columns))
                sel_dtype = st.selectbox("Datatype:", ('datetime64[ns]','Int64','Float64','boolean'))
                if st.button('Apply'):
                    if sel_cols:
                        dataset[sel_cols]=dataset[sel_cols].astype(sel_dtype)
                st.info("**Hint:** Change all date/time columns to *'datetime64[ns]'* datatype.")
    with col2:
        f"Records of '{sel_ds}':"
        st.write(dataset.head())
        f"Statistics of '{sel_ds}':"
        st.write(dataset.describe(include='all'))
    with col3:
        f"Datatypes of '{sel_ds}':"
        dataset.dtypes

