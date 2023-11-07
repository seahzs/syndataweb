import streamlit as st
import pandas as pd
st.set_page_config(page_title='Synthetic Data Web App',layout='wide')

with st.spinner("Loading visualisation libraries, please wait..."):
    import matplotlib.pyplot as plt
    import seaborn as sns

# Loads datasets and models from session state and updates sidebar
datasets=st.session_state['datasets'] if 'datasets' in st.session_state else {}
all_metadata=st.session_state['all_metadata'] if 'all_metadata' in st.session_state else {}
models=st.session_state['models'] if 'models' in st.session_state else {}
syn_datasets=st.session_state['syn_datasets'] if 'syn_datasets' in st.session_state else {}
with st.sidebar:
    with st.expander("Datasets"):
        for dataset in datasets:
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
"### Visualisation - Single Table"
if datasets=={}:
    st.error('Please load datasets to continue.')
else:
    col1, col2 = st.columns([1,4])
    with col1:
        sel_vis = st.radio("Type:", ("Distribution", "Correlation"))
        sel_ds = st.selectbox("Dataset:", options=datasets.keys())
        if sel_ds:
            dataset=datasets[sel_ds]
            if sel_vis=="Distribution":
                sel_feature = st.selectbox('Column *(Feature)*:',sorted(dataset.columns))
            elif sel_vis=="Correlation":
                sel_x = st.selectbox('Feature:',sorted(dataset.columns))
                sel_y = st.selectbox('Group by:',sorted(dataset.columns))
        "---"
        "Comparison with generated data:"
        if sel_ds in syn_datasets:
            sel_ml = st.radio(f"Fitted models for '{sel_ds}':", options=syn_datasets[sel_ds].keys())
            syn_dataset=syn_datasets[sel_ds][sel_ml]
        else:
            st.info("**Hint:** Please fit model and generate data to make a comparison.")
    with col2:
        if sel_vis=="Distribution":
            f"**{sel_ds}** *(Original: {dataset.shape[0]} records)* - Distribution of {sel_feature}"
            with st.spinner('Loading chart, please wait...'):
                plot=sns.displot(dataset.sort_values([sel_feature]), x=sel_feature, stat="percent", common_norm=False, multiple="dodge", aspect=2.5, shrink=.9)
                plot.set(title=f"Distribution of '{sel_feature}'", ylabel="Percentage (%)")
                plt.xticks(rotation=270)
                st.pyplot(plot)
        elif sel_vis=="Correlation":
            f"**{sel_ds}** *(Original: {dataset.shape[0]} records)* - Distribution of {sel_x} grouped by {sel_y}"
            with st.spinner('Loading chart, please wait...'):
                plot=sns.displot(dataset.sort_values([sel_x]), x=sel_x, hue=sel_y, stat="percent", common_norm=False, multiple="dodge", aspect=2.5, shrink=.8)
                plot.set(title=f"Distribution of '{sel_y}' vs '{sel_x}'")
                plt.xticks(rotation=270)
                st.pyplot(plot)
        if sel_ds in syn_datasets:
            if sel_vis=="Distribution":
                f"**{sel_ds}** *(Generated by '{sel_ml}': {syn_dataset.shape[0]} records)* - Distribution of {sel_feature}"
                with st.spinner('Loading chart, please wait...'):
                    plot=sns.displot(syn_dataset.sort_values([sel_feature]), x=sel_feature, stat="percent", common_norm=False, multiple="dodge", aspect=2.5, shrink=.8)
                    plot.set(title=f"Distribution of '{sel_feature}'", ylabel="Percentage (%)")
                    plt.xticks(rotation=270)
                    st.pyplot(plot)
            elif sel_vis=="Correlation":
                f"**{sel_ds}** *(Generated by '{sel_ml}': {syn_dataset.shape[0]} records)* - Distribution of {sel_x} grouped by {sel_y}"
                with st.spinner('Loading chart, please wait...'):
                    plot=sns.displot(syn_dataset.sort_values([sel_x]), x=sel_x, hue=sel_y, stat="percent", common_norm=False, multiple="dodge", aspect=2.5, shrink=.8)
                    plot.set(title=f"Distribution of '{sel_y}' vs '{sel_x}'")
                    plt.xticks(rotation=270)
                    st.pyplot(plot)


        