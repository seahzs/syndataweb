import streamlit as st
import pandas as pd
st.set_page_config(page_title='Synthetic Data Web App',layout='wide')

with st.spinner("Loading ML libraries, please wait..."):
    from sdv.single_table import GaussianCopulaSynthesizer
    from sdv.single_table import CTGANSynthesizer
    from sdv.single_table import CopulaGANSynthesizer
    from sdv.single_table import TVAESynthesizer
    import irg.engine as irgan
    import os
    import shutil
    import json

def convert_irgan_meta(sel_ds, metadata):
    irgan_meta={sel_ds:{"id_cols": [],"attributes": {},"primary_keys": [],"format": "csv"}}
    if 'primary_key' in metadata.to_dict():
        irgan_meta[sel_ds]["primary_keys"].append(metadata.primary_key)
    for (col,dtype) in metadata.columns.items():
        if dtype["sdtype"]=="id":
            irgan_meta[sel_ds]["id_cols"].append(col)
        irgan_meta[sel_ds]["attributes"][col]={"name":col,"type":dtype["sdtype"]}
    return irgan_meta

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
            sel_ml=st.radio("Synthesizer:", ("Copula GAN","CTGAN","Gaussian Copula",'TVAE','IRGAN (not working)'))
            if sel_ml in ("Copula GAN","CTGAN",'TVAE','IRGAN'):
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
                elif sel_ml=="IRGAN (not working)":
                    shutil.rmtree(f'./irgan/single/{sel_ds}', ignore_errors=True)
                    os.makedirs(f'./irgan/single/{sel_ds}/data', exist_ok=True)
                    dataset.to_pickle(f'./irgan/single/{sel_ds}/data/dataset.pkl')
                    with open(f'./irgan/single/{sel_ds}/data/config.json', 'w', encoding='utf-8') as f:
                        json.dump(convert_irgan_meta(sel_ds, metadata), f, ensure_ascii=False, indent=2)
                    augmented_db = irgan.augment(file_path=f'./irgan/single/{sel_ds}/data/config.json', data_dir=f'./irgan/single/{sel_ds}/data', temp_cache=f'./irgan/single/{sel_ds}/temp')
                    # tab_models, deg_models = irgan.train(
                    #     database=augmented_db, do_train=True,
                    #     tab_trainer_args={sel_ds: {'trainer_type': 'CTGAN', 'embedding_dim': 128,
                    #         'gen_optim_lr': 2e-4, 'disc_optim_lr': 2e-4, 'gen_optim_weight_decay': 0, 'disc_optim_weight_decay': 0,
                    #         'gen_scheduler': 'ConstantLR', 'disc_scheduler': 'ConstantLR',
                    #         'ckpt_dir': f'./irgan/single/{sel_ds}/checkpoints', 'log_dir': f'./irgan/single/{sel_ds}/tflog', 'resume': True}},
                    #     deg_trainer_args={}, ser_trainer_args={},
                    #     tab_train_args={sel_ds: {'epochs': sel_epochs, 'batch_size': 200, 'save_freq': 100000}},
                    #     deg_train_args={}, ser_train_args={})
                    # synthesizer = {"tab_models":tab_models, "deg_models": deg_models}
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
