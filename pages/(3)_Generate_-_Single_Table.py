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
        shutil.rmtree(self.directory, ignore_errors=True)
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
single_metadata=st.session_state['single_metadata'] if 'single_metadata' in st.session_state else {}
multi_metadata=st.session_state['multi_metadata'] if 'multi_metadata' in st.session_state else {}
models=st.session_state['models'] if 'models' in st.session_state else {}
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
"### Generate (Single Table)"
if datasets=={} or models=={}:
    st.error('Please load datasets & fit models to continue.')
else:
    col1,col2=st.columns([1,3],gap="medium")
    with col1:
        sel_ds = st.radio("Dataset:", options=models.keys())
        if sel_ds:
            dataset_models=models[sel_ds]
            sel_ml = st.radio("Fitted Model:", options=dataset_models.keys())
            n=datasets[sel_ds].shape[0]
            sel_n = st.number_input(f"Records to generate (real data has {n}):", value=n, format="%i", min_value=0, step=n)
            if st.button("Generate"):
                with col2:
                    with st.spinner('Generating data, please wait...'):
                        syn_data=dataset_models[sel_ml].sample(num_rows=sel_n)
                    if sel_ds not in syn_datasets.keys():
                        syn_datasets[sel_ds]={}
                    syn_datasets[sel_ds][sel_ml]=syn_data
                    st.session_state['syn_datasets']=syn_datasets
                    f"**{sel_ds}** - Preview of generated records using **'{sel_ml}'**"
                    st.write(syn_data.head())
                    f"**{sel_ds}** - Statistics of generated records using **'{sel_ml}'**"
                    st.write(syn_data.describe(include='all'))
            
