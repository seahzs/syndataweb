import streamlit as st
import pandas as pd

#Main Content
st.write("## Generation and Analysis of Synthetic Data")
st.info("To begin, upload a csv file.")

csv_file = st.file_uploader("upload file", type={"csv"})
if csv_file is not None:
    dataset = pd.read_csv(csv_file)
    dataset
