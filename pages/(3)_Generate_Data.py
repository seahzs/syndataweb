import streamlit as st
st.set_page_config(page_title='Synthetic Data Web App',layout='wide')

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
"### Generate Data"
if datasets=={} or (single_models=={} and multi_models=={}):
    st.error('Please load datasets & fit models to continue.')
else:
    col1,col2=st.columns([1,3])
    with col1:
        sel_task = st.radio("Task:",("Generate single table","Generate multiple tables"))
        "---"
        if sel_task=="Generate single table":
            sel_ds = st.radio("Dataset:", options=single_models.keys())
            if sel_ds:
                dataset_models=single_models[sel_ds]
                sel_ml = st.radio("Fitted Model:", options=dataset_models.keys())
                n=datasets[sel_ds].shape[0]
                sel_n = st.number_input(f"Records to generate (real data has {n}):", value=n, format="%i", min_value=0, step=n)
                if st.button("Generate"):
                    with col2:
                        with st.spinner('Generating data, please wait...'):
                            syn_data=dataset_models[sel_ml].sample(num_rows=sel_n)
                        if sel_ds not in single_synthetic.keys():
                            single_synthetic[sel_ds]={}
                        single_synthetic[sel_ds][sel_ml]=syn_data
                        st.session_state['single_synthetic']=single_synthetic
                        f"**{sel_ds}** - Preview of generated records using **'{sel_ml}'**"
                        st.write(syn_data.head())
                        f"**{sel_ds}** - Statistics of generated records using **'{sel_ml}'**"
                        st.write(syn_data.describe(include='all'))
        elif sel_task=="Generate multiple tables":
            with st.expander("Grouped datasets"):
                if multi_metadata:
                    for dataset in multi_metadata['datasets']:
                        f"- {dataset}"
            sel_ml = st.radio("Fitted Model:", options=multi_models.keys())
            if sel_ml=="HMA":
                st.info("**Hint:** Scaling is not available (generated data has same number of records as original).")
            elif sel_ml=="IRGAN":
                sel_scaling=st.number_input(f"Scaling (in multiples of the original records):", value=1, format="%i", min_value=0)
            if sel_ml:
                if st.button("Generate"):
                    with col2:
                        with st.spinner('Generating data, please wait...'):
                            if sel_ml=="HMA":
                                syn_data=multi_models[sel_ml].sample()
                            elif sel_ml=="IRGAN":
                                syn_data=multi_models[sel_ml].sample(scaling=sel_scaling)
                        multi_synthetic[sel_ml]=syn_data
                        st.session_state['multi_synthetic']=multi_synthetic
                        for ds,df in syn_data.items():
                            colA,colB=st.columns([3,1])
                            with colA:
                                f"**{ds}** - Generated using **'{sel_ml}'** *(multiple tables)*"
                                "Preview:"
                                st.write(df.head())
                            with colB:
                                "Statistics:"
                                st.write(df.describe())
                            "---"
