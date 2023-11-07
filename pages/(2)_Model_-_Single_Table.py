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

#synthesizer wrapper for IRGAN
class IRGANSynthesizer():
    def __init__(self, metadata, table_name, epochs):
        self.metadata = metadata
        self.table_name = table_name
        self.epochs = epochs
        self.directory=f'./irgan/single/{self.table_name}'
        self.irgan_meta={self.table_name:{"id_cols": [],"attributes": {},"primary_keys": [],"format": "pickle"}}
        if 'primary_key' in self.metadata.to_dict():
            self.irgan_meta[self.table_name]["primary_keys"].append(self.metadata.primary_key)
        for (col,dtype) in self.metadata.columns.items():
            if dtype["sdtype"]=="id":
                self.irgan_meta[self.table_name]["id_cols"].append(col)
            self.irgan_meta[self.table_name]["attributes"][col]={"name":col,"type":dtype["sdtype"]}
    def fit(self, dataset):
        self.dataset_size=dataset.shape[0]
        shutil.rmtree(self.directory, ignore_errors=True)
        os.makedirs(f'{self.directory}/out', exist_ok=True)
        os.makedirs(f'{self.directory}/data', exist_ok=True)
        dataset.to_pickle(f'{self.directory}/data/{self.table_name}.pkl')
        with open(f'{self.directory}/data/{self.table_name}.json', 'w') as f:
            json.dump(self.irgan_meta, f, indent=2)
        self.augmented_db = irgan.augment(file_path=f'{self.directory}/data/{self.table_name}.json', 
                                        data_dir=f'{self.directory}/data', 
                                        temp_cache=f'{self.directory}/out/temp')
        self.tab_models, self.deg_models = irgan.train(
            database=self.augmented_db, do_train=True,
            tab_trainer_args={sel_ds: {'trainer_type': 'CTGAN', 'embedding_dim': 128,
                'gen_optim_lr': 2e-4, 'disc_optim_lr': 2e-4, 'gen_optim_weight_decay': 0, 'disc_optim_weight_decay': 0,
                'gen_scheduler': 'ConstantLR', 'disc_scheduler': 'ConstantLR',
                'ckpt_dir': f'{self.directory}/out/checkpoints', 'log_dir': f'{self.directory}/out/tflog', 'resume': True}},
            deg_trainer_args={}, ser_trainer_args={},
            tab_train_args={sel_ds: {'epochs': self.epochs, 'batch_size': 200, 'save_freq': 100000}},
            deg_train_args={}, ser_train_args={})
    def sample(self, num_rows):
        self.syn_db = irgan.generate(
            real_db=self.augmented_db, tab_models=self.tab_models, deg_models=self.deg_models,
            save_to=f'{self.directory}/out/generated',
            tab_batch_sizes={self.table_name: 200}, deg_batch_sizes={},
            scaling={self.table_name: num_rows/self.dataset_size},
            save_db_to=f'{self.directory}/out/fake_db', 
            temp_cache=f'{self.directory}/out/temp')
        result=pd.read_csv(f'{self.directory}/out/generated/{self.table_name}.csv')
        shutil.rmtree(f'{self.directory}/out/generated', ignore_errors=True)
        shutil.rmtree(f'{self.directory}/out/fake_db', ignore_errors=True)
        shutil.rmtree(f'{self.directory}/out/temp/generated', ignore_errors=True)
        return result

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
            sel_ml=st.radio("Model *(Synthesizer)*:", ("Copula GAN","CTGAN","Gaussian Copula",'TVAE','IRGAN'))
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
                elif sel_ml=="IRGAN":
                    synthesizer = IRGANSynthesizer(metadata, table_name=sel_ds, epochs=sel_epochs)
                with col2:
                    with st.spinner('Fitting model, this may take several minutes... Please wait.'):
                        synthesizer.fit(dataset)
                    if sel_ds not in models.keys():
                        models[sel_ds]={}
                    models[sel_ds][sel_ml]=synthesizer
                    st.session_state['models']=models
                    f"**{sel_ds}** - Generated sample of 10 records using **'{sel_ml}'**"
                    st.write(synthesizer.sample(num_rows=10))
            st.info("**Hint:** Ensure that metadata is well prepared before modeling.")
