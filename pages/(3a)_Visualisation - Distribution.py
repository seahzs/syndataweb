import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
st.set_page_config(layout='wide')

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
st.write("### Visualisation - Distribution")
col1,col2=st.columns([1,4],gap="medium")
with col1:
    sel_ds = st.selectbox("Select a dataset", options=datasets.keys())
    "---"
    if sel_ds:
        dataset=datasets[sel_ds]
        sel_feature = st.selectbox('Select Feature:',sorted(dataset.columns))
        with col2:
            with st.spinner('Loading chart, please wait...'):
                plot=sns.displot(dataset.sort_values([sel_feature]), x=sel_feature, stat="percent", common_norm=False, multiple="dodge", aspect=2.5)
                plot.set(title=f"Distribution of '{sel_feature}'", ylabel="Percentage (%)")
                plt.xticks(rotation=270)
                st.pyplot(plot)