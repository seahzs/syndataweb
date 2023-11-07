import streamlit as st
import pandas as pd
from sdv.metadata import MultiTableMetadata
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
"### Prepare (Multi Table)"
if datasets=={}:
    st.error('Please load datasets to continue.')
else:
    st.info("Please go to *'(1a) Prepare Single Table'* to set up datatypes and primary keys for each dataset *(table)* before grouping them.")
    col1,col2=st.columns([1,3],gap="medium")
    with col1:
        sel_task = st.radio("Task:", ("Set up grouping", "Add inter-table relationship", "Remove inter-table relationship"))
        "---"
        if sel_task == "Set up grouping":
            sel_multi_ds = st.multiselect("Select ≥2 datasets *(tables)* to group:", options=datasets.keys())
            if st.button("Set grouping"):
                if len(sel_multi_ds)<2:
                    st.error("**Error:** Please select 2 or more datasets.")
                else:
                    multi_meta = {"tables":{}, "relationships":[], "METADATA_SPEC_VERSION":"MULTI_TABLE_V1"}
                    for sel_ds in sel_multi_ds:
                        multi_meta["tables"][sel_ds]={k:v for (k,v) in single_metadata[sel_ds].to_dict().items() if k!="METADATA_SPEC_VERSION"}
                    multi_metadata={'datasets':sel_multi_ds,'metadata':MultiTableMetadata.load_from_dict(multi_meta)}
                    st.session_state['multi_metadata']=multi_metadata
                    with col2:
                        for ds,meta in multi_metadata["metadata"].to_dict()['tables'].items():
                            if "primary_key" in meta.keys():
                                f"**{ds}** - Primary key is *'{meta['primary_key']}'*"
                            else:
                                f'**{ds}** - *No primary key*'
                            st.write(pd.DataFrame.from_dict(meta["columns"]))
                        st.success("Datasets *(tables)* have been grouped. Please add inter-table relationships.")
            st.warning("**Warning:** This will replace the existing grouping and reset inter-table relationships.")
        elif sel_task == "Add inter-table relationship":
            sel_parent=st.radio("Select parent:",multi_metadata['datasets'])
            sel_child=st.radio("Select child *(≠ parent)*:",multi_metadata['datasets'], index=1)
            if sel_parent!=sel_child:
                sel_pri_key=st.selectbox("Select parent's primary key:",datasets[sel_parent].columns)
                sel_fgn_key=st.selectbox("Select child's foreign key:",datasets[sel_child].columns)
                if st.button("Add relationship"):
                    multi_metadata['metadata'].add_relationship(parent_table_name=sel_parent,child_table_name=sel_child,
                                                                parent_primary_key=sel_pri_key,child_foreign_key=sel_fgn_key)
                    st.session_state['multi_metadata']=multi_metadata
            with col2:
                f"List of relationships in grouping *{str(multi_metadata['datasets'])}*"
                st.write(pd.DataFrame.from_records(multi_metadata['metadata'].to_dict()['relationships']))
            st.warning("**Warning:** Parent must have primary key and datatype of child's foreign key must match.")
        elif sel_task == "Remove inter-table relationship":
            sel_parent=st.radio("Select parent:",multi_metadata['datasets'])
            sel_child=st.radio("Select child *(≠ parent)*:",multi_metadata['datasets'], index=1)
            if sel_parent!=sel_child:
                if st.button("Remove relationship"):
                    multi_meta=multi_metadata['metadata'].to_dict()
                    for rship in multi_meta['relationships']:
                        if rship['parent_table_name']==sel_parent and rship['child_table_name']==sel_child:
                            multi_meta['relationships'].remove(rship)
                    multi_metadata['metadata']=MultiTableMetadata.load_from_dict(multi_meta)
                    st.session_state['multi_metadata']=multi_metadata
            with col2:
                f"List of relationships in grouping *{str(multi_metadata['datasets'])}*"
                st.write(pd.DataFrame.from_records(multi_metadata['metadata'].to_dict()['relationships']))