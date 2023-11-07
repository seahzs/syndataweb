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
#Main Content
"### Prepare (Single Table)"
if datasets=={}:
    st.error('Please load datasets to continue.')
else:
    col1,col2=st.columns([1,4],gap="medium")
    with col1:
        sel_task=st.radio("Task:", ("Set datatypes", "Set primary key", "Drop columns"))
        sel_ds = st.radio("Select dataset:", options=datasets.keys())
        "---"
        if sel_ds:
            dataset=datasets[sel_ds]
            metadata=single_metadata[sel_ds]
            if sel_task=="Drop columns":
                to_drop=st.multiselect("Columns to drop:", sorted(dataset.columns))
                if st.button('Apply'):
                    dataset=dataset.drop(columns=to_drop)
                    meta_dict=metadata.to_dict()
                    for col in to_drop:
                        del meta_dict['columns'][col]
                    metadata=SingleTableMetadata.load_from_dict(meta_dict)
                    datasets[sel_ds]=dataset
                    single_metadata[sel_ds]=metadata
                    st.session_state['datasets']=datasets
                    st.session_state['single_metadata']=single_metadata
                st.warning("**Warning:** This action is irreversible, dropped columns cannot be recovered.")
            elif sel_task=="Set datatypes":
                sel_dtype = st.radio("Set datatype:", ('boolean','categorical','datetime','numerical','id','other'))
                sel_cols=st.multiselect("Columns to set:", sorted(dataset.columns))
                if sel_dtype == 'other':
                    oth_dtype = st.selectbox("Other Datatype:", ('address','email','ipv4_address','ipv6_address','mac_address','name','phone_number','ssn','user_agent_string'))
                    pii = st.toggle('sensitive info (to anonymize)')
                if st.button('Apply'):
                    if sel_cols:
                        if sel_dtype=='other':
                            for col in sel_cols:
                                metadata.update_column(column_name=col, sdtype=oth_dtype, pii=pii)
                        else:
                            for col in sel_cols:
                                metadata.update_column(column_name=col, sdtype=sel_dtype)
                    single_metadata[sel_ds]=metadata
                    st.session_state['single_metadata']=single_metadata
                st.info("**Hint:** Change all date/time columns to *'datetime'* datatype.")
            elif sel_task=="Set primary key":
                pri_key_dtypes=('id','address','email','ipv4_address','ipv6_address','mac_address','name','phone_number','ssn','user_agent_string')
                sel_key=st.selectbox("Select primary key:", [col for (col,dtype) in metadata.to_dict()["columns"].items() if dtype["sdtype"] in pri_key_dtypes] )
                if st.button('Apply'):
                    metadata.set_primary_key(sel_key)
                    single_metadata[sel_ds]=metadata
                    st.session_state['single_metadata']=single_metadata
                st.info("**Hint:** Set column datatype as 'id' or 'others' in order to be used as primary key.")
    with col2:
        f"**{sel_ds}** - Preview of records"
        st.write(dataset.head())
        f"**{sel_ds}** - Datatypes (*metadata*):"
        st.write(pd.DataFrame.from_dict(metadata.columns))
        if 'primary_key' in metadata.to_dict():
            st.success(f"Primary key of '{sel_ds}' is set as *'{metadata.to_dict()['primary_key']}'*")

