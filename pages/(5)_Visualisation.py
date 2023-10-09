import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
st.set_page_config(layout='wide')

# Loads datasets and models from session state and updates sidebar
datasets={}
models={}
if 'datasets' not in st.session_state:
    st.error('Please load datasets to continue.')
else:
    datasets=st.session_state['datasets']
if 'models' in st.session_state:
    models=st.session_state['models']
with st.sidebar:
    with st.expander("Datasets"):
        for dataset in datasets:
            f"- {dataset}"
    with st.expander("Models"):
        for dataset_models in models:
            f"{dataset_models}:"
            for model in models[dataset_models]:
                f"- {model}"

#Main Content
st.write("### Visualisation")
col1,col2=st.columns([1,4])
with col1:
    sel_ds = st.selectbox("Dataset:", options=datasets.keys())
    sel_vis = st.selectbox("Type:", ("Distribution", "Correlation"))
    "---"
    if sel_ds:
        dataset=datasets[sel_ds]
        if sel_vis=="Distribution":
            sel_feature = st.selectbox('Feature:',sorted(dataset.columns))
        elif sel_vis=="Correlation":
            sel_x = st.selectbox('Feature <x>:',sorted(dataset.columns))
            sel_y = st.selectbox('Feature <y>:',sorted(dataset.columns))
        with col2:
            if sel_vis=="Distribution":
                with st.spinner('Loading chart, please wait...'):
                    plot=sns.displot(dataset.sort_values([sel_feature]), x=sel_feature, stat="percent", common_norm=False, multiple="dodge", aspect=2.5)
                    plot.set(title=f"Distribution of '{sel_feature}'", ylabel="Percentage (%)")
                    plt.xticks(rotation=270)
                    st.pyplot(plot)
            elif sel_vis=="Correlation":
                with st.spinner('Loading chart, please wait...'):
                    plot=sns.displot(dataset.sort_values([sel_x]), x=sel_x, hue=sel_y, stat="percent", common_norm=False, multiple="dodge", aspect=2.5)
                    plot.set(title=f"Distribution of '{sel_y}' vs '{sel_x}'")
                    plt.xticks(rotation=270)
                    st.pyplot(plot)
        