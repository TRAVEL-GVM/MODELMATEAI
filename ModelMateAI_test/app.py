import os
import pandas as pd
import streamlit as st
import openai

from prompts import *
from config import *
from get_data import *
import openpyxl
from functions import *

df = get_mm_data()

#################################################### BUILD DASHBOARD ############################################

st.set_page_config(page_title=dashboard_main_title, layout="wide")
st.markdown(f"<h1 style='color:{default_color1};'>{dashboard_main_title}</h1>", unsafe_allow_html=True)

st.sidebar.markdown(f'<a><img src="{travel_logo_url}" alt="Logo" style="width: 100%;"></a>', unsafe_allow_html=True)

import numpy as np


if st.checkbox("Show raw data"):
    st.markdown(f"<h6 style='color:#4CAF50;'>Raw data</h6>", unsafe_allow_html=True)
    st.header("Data Overview")

    st.write(f" ")
    st.write(f"Shape of the DataFrame: {df.shape[0]} rows, {df.shape[1]} columns")

    st.markdown("#### Unique values and % of categorical columns:")

    display_dataframe_as_html_table(show_all_categorical_summary(df),  min_column_widths={
        'Detetor': 140,
        'Sponsor - Dependentes': 150,
        'Sponsor - Área Funcional': 300,
        'Âmbito do Modelo': 130,
        'Natureza da Medida': 220,
        'Parâmetro': 200,
        'Status de Modelo': 250,
        'Severidade': 170,
        'Tipo de Deadline': 170,
        'Status': 170,
        'Observações - Detetor': 1500})

    st.write('')
    st.markdown("#### Summary statistics about numeric statistics:")

    display_dataframe_as_html_table(df.describe().reset_index(names='').drop(columns=['ID']))

    st.markdown("#### Raw data:")
    #display_dataframe_as_html_table(df)
    st.dataframe(df, hide_index=True)

st.sidebar.header("Select index:")
indicator = st.sidebar.selectbox(
    "Choose an indicator to analyse:", sidebar_indicators
)


st.title("ModelMate GPT")

query = st.text_input("Make a question about ModelMate:")

if query:
    response = ask_question_to_dataframe(query, df)

    st.write("Answer:")
    st.write(response)


