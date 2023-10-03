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


#Main Content
st.write("### Visualisation (Single)")
st.write("#### Feature Selection")
sel_year = st.selectbox('Select Year:',datasets.keys())
if sel_year:
    dataset=datasets[sel_year]
    sel_feat = st.selectbox('Select Feature to Visualize:',dataset.columns)
    "---"
    st.write("#### Scope Filtering")
    sel_filter = st.selectbox('Select Feature to Filter:',dataset.columns)
    if sel_filter:
        counts=dataset[sel_filter].value_counts()
        sel_range = st.multiselect('Select Range:',counts.index)
        "---"
        st.write("#### Visualisation")
        if sel_year and sel_feat:
            with st.spinner('Loading chart, please wait...'):
                dataset=dataset[dataset[sel_filter].isin(sel_range)]
                st.bar_chart(dataset[sel_feat].value_counts())