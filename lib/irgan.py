import pandas as pd
import irg.engine as irgan
import os
import shutil
import json
import warnings
warnings.filterwarnings('ignore')

#synthesizer wrapper for IRGAN single table
class SingleIRGANSynthesizer():
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
            tab_trainer_args={self.table_name: {'trainer_type': 'CTGAN', 'embedding_dim': 128,
                'gen_optim_lr': 2e-4, 'disc_optim_lr': 2e-4, 'gen_optim_weight_decay': 0, 'disc_optim_weight_decay': 0,
                'gen_scheduler': 'ConstantLR', 'disc_scheduler': 'ConstantLR',
                'ckpt_dir': f'{self.directory}/out/checkpoints', 'log_dir': f'{self.directory}/out/tflog', 'resume': True}},
            deg_trainer_args={}, ser_trainer_args={},
            tab_train_args={self.table_name: {'epochs': self.epochs, 'batch_size': 200, 'save_freq': 100000}},
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
    
#synthesizer wrapper for IRGAN multi table
class MultiIRGANSynthesizer():
    def __init__(self, metadata, epochs):
        self.metadata = metadata
        self.table_names = {}
        self.epochs = epochs
        self.directory='./irgan/multi/'
        shutil.rmtree(self.directory, ignore_errors=True)
        self.irgan_meta={}
        for table_name,table_meta in self.metadata["tables"].items():
            self.irgan_meta[table_name]={"id_cols": [],"attributes": {},"primary_keys": [],"foreign_keys": [],"format": "pickle"}
            if 'primary_key' in table_meta:
                self.irgan_meta[table_name]["primary_keys"].append(table_meta['primary_key'])
            for (col,dtype) in table_meta['columns'].items():
                if dtype["sdtype"]=="id":
                    self.irgan_meta[table_name]["id_cols"].append(col)
                if dtype["sdtype"]=="datetime":
                    self.irgan_meta[table_name]["attributes"][col]={"name":col,"type":dtype["sdtype"],"date_format":''}
                else:
                    self.irgan_meta[table_name]["attributes"][col]={"name":col,"type":dtype["sdtype"]}
        # for rship in self.metadata["relationships"]:
        #     self.irgan_meta[rship["child_table_name"]]["foreign_keys"].append({"columns": [rship["child_foreign_key"]],
        #                                                                        "parent": rship["parent_table_name"]})
    def fit(self, datasets):
        self.table_names=datasets.keys()
        shutil.rmtree(self.directory, ignore_errors=True)
        os.makedirs(f'{self.directory}/out', exist_ok=True)
        os.makedirs(f'{self.directory}/data', exist_ok=True)
        for (table_name,dataset) in datasets.items():
            dataset.to_pickle(f'{self.directory}/data/{table_name}.pkl')
        with open(f'{self.directory}/data/config.json', 'w') as f:
            json.dump(self.irgan_meta, f, indent=2)
        self.augmented_db = irgan.augment(file_path=f'{self.directory}/data/config.json', 
                                        data_dir=f'{self.directory}/data', 
                                        temp_cache=f'{self.directory}/out/temp',
                                        mtype='affecting')
        # self.augmented_db = irgan.augment(file_path='./irgan/alset_config.json', 
        #                                 data_dir=f'{self.directory}/data', 
        #                                 temp_cache=f'{self.directory}/out/temp',
        #                                 mtype='affecting')
        self.tab_models, self.deg_models = irgan.train(
            database=self.augmented_db, do_train=True,
            tab_trainer_args={table_name: {'trainer_type': 'CTGAN', 'embedding_dim': 128, 'gen_optim_lr': 2e-4, 'disc_optim_lr': 2e-4,
                                            'gen_optim_weight_decay': 0, 'disc_optim_weight_decay': 0,
                                            'gen_scheduler': 'ConstantLR', 'disc_scheduler': 'ConstantLR',
                                            'ckpt_dir': f'{self.directory}/out/tab-checkpoints',
                                            'log_dir': f'{self.directory}/out/tab-tflog', 
                                            'resume': True} for table_name in self.table_names},
            deg_trainer_args={table_name: {'trainer_type': 'stepped','lr': 2e-4,'optim_weight_decay': 0,'scheduler': 'ConstantLR',
                                            'ckpt_dir': f'{self.directory}/out/deg-checkpoints','log_dir': f'{self.directory}/out/deg-tflog',
                                            'resume': True} for table_name in self.table_names}, 
            ser_trainer_args={},
            tab_train_args={table_name: {'epochs': self.epochs, 'batch_size': 200, 'save_freq': 100000} for table_name in self.table_names},
            deg_train_args={table_name: {'epochs': self.epochs, 'batch_size': 200, 'save_freq': 100000} for table_name in self.table_names}, 
            ser_train_args={})
    def sample(self):
        self.syn_db = irgan.generate(
            real_db=self.augmented_db, tab_models=self.tab_models, deg_models=self.deg_models,
            save_to=f'{self.directory}/out/generated',
            tab_batch_sizes={table_name: 200 for table_name in self.table_names}, 
            deg_batch_sizes={},
            save_db_to=f'{self.directory}/out/fake_db', 
            temp_cache=f'{self.directory}/out/temp')
        result={table_name: pd.read_csv(f'{self.directory}/out/generated/{table_name}.csv') for table_name in self.table_names}
        shutil.rmtree(f'{self.directory}/out/generated', ignore_errors=True)
        shutil.rmtree(f'{self.directory}/out/fake_db', ignore_errors=True)
        shutil.rmtree(f'{self.directory}/out/temp/generated', ignore_errors=True)
        return result