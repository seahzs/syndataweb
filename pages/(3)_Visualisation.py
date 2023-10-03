import streamlit as st
import pandas as pd

# Loads dataset and updates dataset list in sidebar
datasets = {}
with st.sidebar:
    for dataset_name in ('Survey 2020', 'Survey 2021', 'Survey 2022'):
        if dataset_name in st.session_state:
            datasets[dataset_name]=st.session_state[dataset_name]
    st.write('**Loaded Datasets:**')
    st.info(", ".join(datasets.keys()))

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