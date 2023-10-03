import streamlit as st
import pandas as pd

#Initialise collection of datasets
datasets = {}

# Main Content
st.write("### Load Datasets")
st.write("Please select the dataset(s) to be loaded.")
survey_data={'Survey 2020':'./data/kaggle_survey_2020_responses.csv',
            'Survey 2021':'./data/kaggle_survey_2021_responses.csv',
            'Survey 2022':'./data/kaggle_survey_2022_responses.csv'}
responses = {}
for survey in survey_data.keys():
    responses[survey] = st.checkbox(survey, True)
if st.button('Load Selected'):
    "---"
    with st.spinner('Loading datasets, please wait...'):
        for survey, to_use in responses.items():
            if to_use:
                datasets[survey] = pd.read_csv(survey_data[survey], skiprows=[0])
                st.session_state[survey] = datasets[survey]
                with st.expander(f'{survey} loaded.'):
                    datasets[survey].shape
                    st.write(datasets[survey].head())
            elif survey in st.session_state:
                del st.session_state[survey]
    with st.sidebar:
        st.write('**Loaded Datasets:**')
        st.info(", ".join(datasets.keys()))
    st.success("Please proceed to ***'(2) Data Preparation'*** page on the sidebar.")