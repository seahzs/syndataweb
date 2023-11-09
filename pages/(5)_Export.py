import streamlit as st
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
        for model in multi_models:
            f"- {model}"
    with st.expander("Generated Data - Single Table"):
        for syn_dataset in syn_datasets:
            f"{syn_dataset}:"
            for model_gen in syn_datasets[syn_dataset]:
                f"- {model_gen}"

#Main Content
"### Export Synthetic Data"
if datasets=={} or single_models=={}:
    st.error('Please load datasets & fit models to continue.')
else:
    col1,col2=st.columns([1,3],gap="medium")
    with col1:
        sel_ds = st.radio("Synthetic Dataset:", options=syn_datasets.keys())
        if sel_ds:
            sel_ml = st.radio("Fitted Model:", options=syn_datasets[sel_ds].keys())
            syn_dataset=syn_datasets[sel_ds][sel_ml]
        st.download_button("Download CSV file",syn_dataset.to_csv(index=False).encode('utf-8'),f"{sel_ds}_{sel_ml}.csv","text/csv",key='download-csv')
        with col2:
            f"**{sel_ds}** - Preview of generated records using **'{sel_ml}'**"
            st.write(syn_dataset.head(3))
            f"**{sel_ds}** - Statistics of generated records using **'{sel_ml}'**"
            st.write(syn_dataset.describe(include='all'))