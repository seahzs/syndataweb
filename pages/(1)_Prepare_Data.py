import streamlit as st
st.set_page_config(page_title='Synthetic Data Web App',layout='wide')
import pandas as pd
from sdv.metadata import SingleTableMetadata
from sdv.metadata import MultiTableMetadata

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

#Main Content
"### Prepare Data"
if datasets=={}:
    st.error('Please load tables to continue.')
else:
    col1,col2=st.columns([1,3])
    with col1:
        sel_task=st.radio("Task:", ("Set datatype", "Set/remove primary key", "Drop column", 
                                    "Group tables", "Add/remove inter-table relationship"))
        "---"
        if sel_task in ("Set datatype", "Set/remove primary key", "Drop column"):
            sel_ds = st.selectbox("Select table:", options=datasets.keys())
            if sel_ds:
                dataset=datasets[sel_ds]
                metadata=single_metadata[sel_ds]
                if sel_task=="Set datatype":
                    sel_cols=st.multiselect("Select columns:", dataset.columns)
                    sel_dtype = st.radio("Select datatype:", ('boolean','categorical','datetime','numerical','id','other'))
                    if sel_dtype == 'datetime':
                        dt_format = st.radio("Date-time format:", ("default: datetime64","date: yyyy-mm-dd","time: hh:mm:ss",
                                                                       "both: yyyy-mm-dd hh:mm:ss"))
                    if sel_dtype == 'numerical':
                        num_format = st.radio("Numerical format:", ("integer","float"))
                    elif sel_dtype == 'other':
                        oth_dtype = st.selectbox("Other Datatype:", ('address','email','ipv4_address','ipv6_address','mac_address',
                                                                     'name','phone_number','ssn','user_agent_string'))
                        pii = st.toggle('sensitive info (to anonymize)')
                    if st.button('Set datatype'):
                        if sel_cols:
                            if sel_dtype=='other':
                                for col in sel_cols:
                                    metadata.update_column(column_name=col, sdtype=oth_dtype, pii=pii)
                            elif sel_dtype=='datetime':
                                if dt_format=='default: datetime64':
                                    for col in sel_cols:
                                        metadata.update_column(column_name=col, sdtype=sel_dtype)
                                        dataset[col]=pd.to_datetime(dataset[col])
                                else:
                                    dt_map={'date: yyyy-mm-dd':"%Y-%m-%d",'time: hh:mm:ss':"%H:%M:%S",
                                            'both: yyyy-mm-dd hh:mm:ss':"%Y-%m-%d %H:%M:%S"}
                                    for col in sel_cols:
                                        metadata.update_column(column_name=col, sdtype=sel_dtype, datetime_format=dt_map[dt_format])
                                        dataset[col]=pd.to_datetime(dataset[col]).dt.strftime(dt_map[dt_format])
                            elif sel_dtype=='numerical':
                                for col in sel_cols:
                                    dataset[col]=dataset[col].astype({"integer":"Int64","float":"Float64"}[num_format])
                                    metadata.update_column(column_name=col, sdtype=sel_dtype)
                            else:
                                for col in sel_cols:
                                    metadata.update_column(column_name=col, sdtype=sel_dtype)
                            single_metadata[sel_ds]=metadata
                            st.session_state['single_metadata']=single_metadata
                            datasets[sel_ds]=dataset
                            st.session_state['datasets']=datasets
                            if multi_metadata and sel_ds in multi_metadata["datasets"]:
                                multi_metadata["metadata"]["tables"][sel_ds]={k:v for (k,v) in single_metadata[sel_ds].to_dict().items() if k!="METADATA_SPEC_VERSION"}
                                st.session_state['multi_metadata']=multi_metadata
                        st.success(f"Columns {sel_cols} has been set as '{sel_dtype}'.")
                    st.info("**Hint:** Change all date/time columns to *'datetime'* datatype.")
                elif sel_task=="Set/remove primary key":
                    meta=metadata.to_dict()
                    if 'primary_key' in meta.keys():
                        if st.button('Remove primary key'):
                            del meta['primary_key']
                            metadata=SingleTableMetadata.load_from_dict(meta)
                            single_metadata[sel_ds]=metadata
                            st.session_state['single_metadata']=single_metadata
                            if multi_metadata and sel_ds in multi_metadata["datasets"]:
                                del multi_metadata["metadata"]["tables"][sel_ds]["primary_key"]
                                st.session_state['multi_metadata']=multi_metadata
                            st.success("Primary key removed.")
                    pri_key_dtypes=('id','address','email','ipv4_address','ipv6_address',
                                    'mac_address','name','phone_number','ssn','user_agent_string')
                    sel_key=st.selectbox("Select column:", [col for (col,dtype) in metadata.to_dict()["columns"].items() if dtype["sdtype"] in pri_key_dtypes] )
                    if st.button('Set primary key'):
                        metadata.set_primary_key(sel_key)
                        single_metadata[sel_ds]=metadata
                        st.session_state['single_metadata']=single_metadata
                        if multi_metadata and sel_ds in multi_metadata["datasets"]:
                            multi_metadata["metadata"]["tables"][sel_ds]["primary_key"]=sel_key
                            st.session_state['multi_metadata']=multi_metadata
                        st.success("Primary key updated.")
                    st.info("**Hint:** Set column datatype as 'id' or 'others' in order to be used as primary key.")
                elif sel_task=="Drop column":
                    to_drop=st.multiselect("Select columns:", dataset.columns)
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
                        st.success(f"Columns {to_drop} have been dropped.")
                    st.warning("**Warning:** This action is irreversible, dropped columns cannot be recovered.")
            with col2:
                f"**{sel_ds}** - Preview"
                st.write(dataset.head())
                f"**{sel_ds}** - Datatypes (*metadata*)"
                st.write(pd.DataFrame.from_dict(metadata.columns))
                f"**{sel_ds}** - Datatypes (*dataframe table*)"
                st.write(dataset.dtypes.to_frame().rename(columns={0:"sdtype"}).transpose())
                if 'primary_key' in metadata.to_dict():
                    st.info(f"Primary key of '{sel_ds}' is set as *'{metadata.to_dict()['primary_key']}'*")
                
        elif sel_task == "Group tables":
            "Select tables:"
            sel_multi_ds = {sel_ds:st.checkbox(sel_ds) for sel_ds in datasets.keys()}
            if st.button("Group tables"):
                sel_multi_ds = [sel_ds for sel_ds,is_selected in sel_multi_ds.items() if is_selected]
                if len(sel_multi_ds)<2:
                    st.error("**Error:** Please select 2 or more tables.")
                else:
                    multi_meta = {"tables":{}, "relationships":[], "METADATA_SPEC_VERSION":"MULTI_TABLE_V1"}
                    for sel_ds in sel_multi_ds:
                        multi_meta["tables"][sel_ds]={k:v for (k,v) in single_metadata[sel_ds].to_dict().items() if k!="METADATA_SPEC_VERSION"}
                    multi_metadata={'datasets':sel_multi_ds,'metadata':multi_meta}
                    st.session_state['multi_metadata']=multi_metadata
                    st.success(f"Tables {sel_ds} have been grouped. Please add inter-table relationships.")
            with col2:
                for sel_ds in sel_multi_ds:
                    if "primary_key" in single_metadata[sel_ds].to_dict():
                        f"**{sel_ds}** - Primary key is *'{single_metadata[sel_ds].to_dict()['primary_key']}'*"
                    else:
                        f'**{sel_ds}** - *No primary key*'
                    st.write(pd.DataFrame.from_dict(single_metadata[sel_ds].to_dict()["columns"]))
            st.warning("**Warning:** Please set up datatypes and primary keys before grouping. Existing grouping will be replaced.")
        elif sel_task == "Add/remove inter-table relationship":
            if multi_metadata=={}:
                st.error('Please group tables first.')
            else:
                sel_parent=st.radio("Select parent:",multi_metadata['datasets'])
                sel_child=st.radio("Select child *(≠ parent)*:",multi_metadata['datasets'], index=1)
                if sel_parent!=sel_child:
                    rship_exists=False
                    multi_meta=multi_metadata['metadata']
                    for rship in multi_meta['relationships']:
                        if rship['parent_table_name']==sel_parent and rship['child_table_name']==sel_child:
                            rship_exists=True
                        elif rship['parent_table_name']==sel_child and rship['child_table_name']==sel_parent:
                            rship_exists=True
                    if rship_exists:
                        if st.button("Remove relationship"):
                            multi_meta['relationships'].remove(rship)
                            multi_metadata['metadata']=multi_meta
                            st.session_state['multi_metadata']=multi_metadata
                            st.success(f"Relationship for tables {sel_parent} and {sel_child} removed.")
                    sel_pri_key=st.selectbox("Select parent's primary key:",datasets[sel_parent].columns)
                    sel_fgn_key=st.selectbox("Select child's foreign key:",datasets[sel_child].columns)
                    if st.button("Add relationship"):
                        if not rship_exists:
                            multi_meta=MultiTableMetadata.load_from_dict(multi_meta)
                            multi_meta.add_relationship(parent_table_name=sel_parent,child_table_name=sel_child,
                                                        parent_primary_key=sel_pri_key,child_foreign_key=sel_fgn_key)
                            multi_meta=multi_meta.to_dict()
                            multi_metadata['metadata']=multi_meta
                            st.session_state['multi_metadata']=multi_metadata
                            st.success(f"Relationship added for tables '{sel_parent}' and '{sel_child}'.")
                        else:
                            st.error(f"Relationship for tables {sel_parent} and {sel_child} exists!")
                st.warning("**Warning:** Parent must have primary key and datatype of child's foreign key must match.")
                with col2:
                    f"List of relationships in grouping *{str(multi_metadata['datasets'])}*"
                    st.write(pd.DataFrame.from_records(multi_metadata['metadata']['relationships']))
