import streamlit as st
st.set_page_config(page_title='Synthetic Data Web App',layout='wide')
import pandas as pd

with st.spinner("Loading ML libraries, please wait..."):
    from sdv.metadata import MultiTableMetadata
    from sdv.single_table import GaussianCopulaSynthesizer
    from sdv.single_table import CTGANSynthesizer
    from sdv.single_table import CopulaGANSynthesizer
    from sdv.single_table import TVAESynthesizer
    from sdv.multi_table import HMASynthesizer
    from lib.irgan import SingleIRGANSynthesizer,MultiIRGANSynthesizer
    import warnings
    warnings.simplefilter(action='ignore', category=FutureWarning)

# Loads datasets and models from session state and updates sidebar
datasets=st.session_state['datasets'] if 'datasets' in st.session_state else {}
single_metadata=st.session_state['single_metadata'] if 'single_metadata' in st.session_state else {}
multi_metadata=st.session_state['multi_metadata'] if 'multi_metadata' in st.session_state else {}
single_models=st.session_state['single_models'] if 'single_models' in st.session_state else {}
multi_models=st.session_state['multi_models'] if 'multi_models' in st.session_state else {}
single_synthetic=st.session_state['single_synthetic'] if 'single_synthetic' in st.session_state else {}
multi_synthetic=st.session_state['multi_synthetic'] if 'multi_synthetic' in st.session_state else {}
with st.sidebar:
    with st.expander("Datasets"):
        for dataset in datasets:
            f"- {dataset}"
    with st.expander("Grouped Datasets"):
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
"### Model (Training)"
#st.write(multi_metadata["metadata"])
if datasets=={}:
    st.error('Please load datasets to continue.')
else:
    col1,col2=st.columns([1,3])
    with col1:
        sel_task=st.radio("Task:", ("Model single table", "Model multiple tables *(grouped)*"))
        "---"
        if sel_task=="Model single table":
            sel_ds = st.selectbox("Select dataset:", options=datasets.keys())
            if sel_ds:
                dataset=datasets[sel_ds]
                metadata = single_metadata[sel_ds]
                with st.expander("Show metadata (*datatypes*):"):
                    if 'primary_key' in metadata.to_dict():
                        f"Primary key: *'{metadata.to_dict()['primary_key']}'*"
                    st.write(pd.DataFrame.from_dict(metadata.columns).transpose().reset_index())
                sel_ml=st.radio("Select model *(synthesizer)*:", ("Copula GAN","CTGAN","Gaussian Copula",'TVAE','IRGAN'))
                if sel_ml in ("Copula GAN","CTGAN",'TVAE','IRGAN'):
                    sel_epochs=st.number_input('Epochs (*training cycles*):', value=1, format="%i", min_value=1)
                if st.button("Fit model"):
                    if sel_ml=="Gaussian Copula":
                        synthesizer = GaussianCopulaSynthesizer(metadata)
                    elif sel_ml=="CTGAN":
                        synthesizer = CTGANSynthesizer(metadata, epochs=sel_epochs)
                    elif sel_ml=="Copula GAN":
                        synthesizer = CopulaGANSynthesizer(metadata, epochs=sel_epochs)
                    elif sel_ml=="TVAE":
                        synthesizer = TVAESynthesizer(metadata, epochs=sel_epochs)
                    elif sel_ml=="IRGAN":
                        synthesizer = SingleIRGANSynthesizer(metadata, table_name=sel_ds, epochs=sel_epochs)
                    with col2:
                        with st.spinner('Fitting model, this may take several minutes... Please wait.'):
                            synthesizer.fit(dataset)
                            if sel_ds not in single_models.keys():
                                single_models[sel_ds]={}
                            single_models[sel_ds][sel_ml]=synthesizer
                            st.session_state['single_models']=single_models
                            f"**{sel_ds}** - Generated sample of 10 records using **'{sel_ml}'**"
                            st.write(synthesizer.sample(num_rows=10))
                st.info("**Hint:** Ensure that metadata is well prepared before modeling.")
        elif sel_task=="Model multiple tables *(grouped)*":
            if multi_metadata:
                metadata=MultiTableMetadata.load_from_dict(multi_metadata['metadata'])
                multi_datasets={ds:datasets[ds] for ds in multi_metadata['datasets']}
                with st.expander("Grouped datasets"):
                    if multi_metadata:
                        for dataset in multi_metadata['datasets']:
                            f"- {dataset}"
                sel_ml=st.radio("Select model *(synthesizer)*:", ("HMA","IRGAN"))
                if sel_ml =='IRGAN':
                    sel_epochs=st.number_input('Epochs (*training cycles*):', value=1, format="%i", min_value=1)
                if st.button("Fit model"):
                    if sel_ml=="HMA":
                        synthesizer = HMASynthesizer(metadata)
                    elif sel_ml=="IRGAN":
                        synthesizer = MultiIRGANSynthesizer(multi_metadata['metadata'], epochs=sel_epochs)
                    with col2:
                        with st.spinner('Fitting model, this may take several minutes... Please wait.'):
                            synthesizer.fit(multi_datasets)
                            multi_models[sel_ml]=synthesizer
                            st.session_state['multi_models']=multi_models
                            st.success(f"Grouped tables has been fitted for {sel_ml}. Please proceed to generate data.")
                st.info("**Hint:** Ensure that inter-table relationships are well prepared before modeling.")
            else:
                st.error('Please group datasets *(tables)* first.')
