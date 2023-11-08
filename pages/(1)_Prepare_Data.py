import streamlit as st
import pandas as pd
from sdv.metadata import SingleTableMetadata
from sdv.metadata import MultiTableMetadata
st.set_page_config(page_title='Synthetic Data Web App',layout='wide')

# Loads datasets and models from session state and updates sidebar
datasets=st.session_state['datasets'] if 'datasets' in st.session_state else {}
single_metadata=st.session_state['single_metadata'] if 'single_metadata' in st.session_state else {}
multi_metadata=st.session_state['multi_metadata'] if 'multi_metadata' in st.session_state else {}
single_models=st.session_state['single_models'] if 'single_models' in st.session_state else {}
multi_models=st.session_state['multi_models'] if 'multi_models' in st.session_state else {}
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
        for dataset_models in single_models:
            f"{dataset_models}:"
            for model in single_models[dataset_models]:
                f"- {model}"
    with st.expander("Fitted Models - Multiple Tables"):
        for models in multi_models:
            f"- {model}"
    with st.expander("Generated Data - Single Table"):
        for syn_dataset in syn_datasets:
            f"{syn_dataset}:"
            for model_gen in syn_datasets[syn_dataset]:
                f"- {model_gen}"

#Main Content
"### Prepare Data"
if datasets=={}:
    st.error('Please load datasets to continue.')
else:
    col1,col2=st.columns([1,3],gap="medium")
    with col1:
        sel_task=st.radio("Task:", ("Set datatypes", "Set primary key", "Remove primary key", "Drop columns", "Group datasets", "Add inter-table relationship", "Remove inter-table relationship"))
        "---"
        if sel_task in ("Set datatypes", "Set primary key", "Remove primary key", "Drop columns"):
            sel_ds = st.radio("Select dataset:", options=datasets.keys())
            if sel_ds:
                dataset=datasets[sel_ds]
                metadata=single_metadata[sel_ds]
                if sel_task=="Set datatypes":
                    sel_dtype = st.radio("Select datatype:", ('boolean','categorical','datetime','numerical','id','other'))
                    if sel_dtype == 'other':
                        oth_dtype = st.selectbox("Other Datatype:", ('address','email','ipv4_address','ipv6_address','mac_address','name','phone_number','ssn','user_agent_string'))
                        pii = st.toggle('sensitive info (to anonymize)')
                    sel_cols=st.multiselect("Select columns:", sorted(dataset.columns))
                    if st.button('Set datatype'):
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
                    sel_key=st.selectbox("Select column:", [col for (col,dtype) in metadata.to_dict()["columns"].items() if dtype["sdtype"] in pri_key_dtypes] )
                    if st.button('Set primary key'):
                        metadata.set_primary_key(sel_key)
                        single_metadata[sel_ds]=metadata
                        st.session_state['single_metadata']=single_metadata
                    st.info("**Hint:** Set column datatype as 'id' or 'others' in order to be used as primary key.")
                elif sel_task=="Remove primary key":
                    if st.button('Remove primary key'):
                        meta=metadata.to_dict()
                        del meta['primary_key']
                        metadata=SingleTableMetadata.load_from_dict(meta)
                        single_metadata[sel_ds]=metadata
                        st.session_state['single_metadata']=single_metadata
                    st.info("**Hint:** Set column datatype as 'id' or 'others' in order to be used as primary key.")
                elif sel_task=="Drop columns":
                    to_drop=st.multiselect("Select columns:", sorted(dataset.columns))
                    if st.button('Drop columns'):
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
            with col2:
                f"**{sel_ds}** - Preview"
                st.write(dataset.head())
                f"**{sel_ds}** - Datatypes (*metadata*)"
                st.write(pd.DataFrame.from_dict(metadata.columns))
                if 'primary_key' in metadata.to_dict():
                    st.info(f"Primary key of '{sel_ds}' is set as *'{metadata.to_dict()['primary_key']}'*")
        elif sel_task == "Group datasets":
            st.warning("**Warning:** Please set up datatypes and primary keys before grouping. Existing grouping will be replaced.")
            sel_multi_ds = st.multiselect("Select ≥2 datasets *(tables)* to group:", options=datasets.keys())
            if st.button("Group datasets"):
                if len(sel_multi_ds)<2:
                    st.error("**Error:** Please select 2 or more datasets.")
                else:
                    multi_meta = {"tables":{}, "relationships":[], "METADATA_SPEC_VERSION":"MULTI_TABLE_V1"}
                    for sel_ds in sel_multi_ds:
                        multi_meta["tables"][sel_ds]={k:v for (k,v) in single_metadata[sel_ds].to_dict().items() if k!="METADATA_SPEC_VERSION"}
                    multi_metadata={'datasets':sel_multi_ds,'metadata':MultiTableMetadata.load_from_dict(multi_meta)}
                    st.session_state['multi_metadata']=multi_metadata
                    st.success("Datasets *(tables)* have been grouped. Please add inter-table relationships.")
            
            with col2:
                for sel_ds in sel_multi_ds:
                    if "primary_key" in single_metadata[sel_ds].to_dict():
                        f"**{sel_ds}** - Primary key is *'{single_metadata[sel_ds].to_dict()['primary_key']}'*"
                    else:
                        f'**{sel_ds}** - *No primary key*'
                    st.write(pd.DataFrame.from_dict(single_metadata[sel_ds].to_dict()["columns"]))
        elif sel_task == "Add inter-table relationship":
            if multi_metadata:
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
            else:
                st.error('Please group datasets *(tables)* first.')
        elif sel_task == "Remove inter-table relationship":
            if multi_metadata:
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
            else:
                st.error('Please group datasets *(tables)* first.')
