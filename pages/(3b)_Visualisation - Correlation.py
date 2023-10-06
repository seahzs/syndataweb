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
st.write("### Visualisation - Correlation")
col1,col2=st.columns([1,4],gap="medium")
with col1:
    sel_ds = st.selectbox("Select a dataset", options=datasets.keys())
    "---"
    if sel_ds:
        dataset=datasets[sel_ds]
        sel_x = st.selectbox('Select Feature <x>:',sorted(dataset.columns))
        sel_y = st.selectbox('Select Feature <y>:',sorted(dataset.columns))
        with col2:
            with st.spinner('Loading chart, please wait...'):
                plot=sns.displot(dataset.sort_values([sel_x]), x=sel_x, hue=sel_y, stat="percent", common_norm=False, multiple="dodge", aspect=2.5)
                plot.set(title=f"Distribution of '{sel_y}' vs '{sel_x}'")
                plt.xticks(rotation=270)
                st.pyplot(plot)