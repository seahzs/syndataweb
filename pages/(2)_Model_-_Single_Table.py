import streamlit as st
import pandas as pd
st.set_page_config(page_title='Synthetic Data Web App',layout='wide')

with st.spinner("Loading ML libraries, please wait..."):
    from sdv.single_table import GaussianCopulaSynthesizer
    from sdv.single_table import CTGANSynthesizer
    from sdv.single_table import CopulaGANSynthesizer
    from sdv.single_table import TVAESynthesizer

# Loads datasets and models from session state and updates sidebar
datasets=st.session_state['datasets'] if 'datasets' in st.session_state else {}
all_metadata=st.session_state['all_metadata'] if 'all_metadata' in st.session_state else {}
models=st.session_state['models'] if 'models' in st.session_state else {}
syn_datasets=st.session_state['syn_datasets'] if 'syn_datasets' in st.session_state else {}
with st.sidebar:
    with st.expander("Datasets"):
        for dataset in datasets:
            f"- {dataset}"
    with st.expander("Fitted Models"):
        for dataset_models in models:
            f"{dataset_models}:"
            for model in models[dataset_models]:
                f"- {model}"
    with st.expander("Synthetic Data"):
        for syn_dataset in syn_datasets:
            f"{syn_dataset}:"
            for model_gen in syn_datasets[syn_dataset]:
                f"- {model_gen}"

#Main Content
"### Modeling (Single Table)"
if datasets=={}:
    st.error('Please load datasets to continue.')
else:
    col1,col2=st.columns([1,3],gap="medium")
    with col1:
        sel_ds = st.selectbox("Dataset:", options=datasets.keys())
        if sel_ds:
            dataset=datasets[sel_ds]
            metadata = all_metadata[sel_ds]
            with st.expander("Show metadata (*datatypes*):"):
                if 'primary_key' in metadata.to_dict():
                    f"Primary key: *'{metadata.to_dict()['primary_key']}'*"
                st.write(pd.DataFrame.from_dict(metadata.columns).transpose())
            sel_ml=st.radio("Synthesizer:", ("Copula GAN","CTGAN","Gaussian Copula",'TVAE'))
            if sel_ml in ("Copula GAN","CTGAN",'TVAE'):
                sel_epochs=st.slider('Epochs (*training cycles*):', 1, 300)
            if st.button("Fit model"):
                if sel_ml=="Gaussian Copula":
                    synthesizer = GaussianCopulaSynthesizer(metadata)
                elif sel_ml=="CTGAN":
                    synthesizer = CTGANSynthesizer(metadata, epochs=sel_epochs)
                elif sel_ml=="Copula GAN":
                    synthesizer = CopulaGANSynthesizer(metadata, epochs=sel_epochs)
                elif sel_ml=="TVAE":
                    synthesizer = TVAESynthesizer(metadata, epochs=sel_epochs)
                with col2:
                    with st.spinner('Fitting model, please wait...'):
                        synthesizer.fit(dataset)
                    if sel_ds not in models.keys():
                        models[sel_ds]={}
                    models[sel_ds][sel_ml]=synthesizer
                    st.session_state['models']=models
                    "Generated Sample:"
                    st.write(synthesizer.sample(num_rows=10))
            st.info("**Hint:** Ensure that metadata is well prepared before modeling.")
