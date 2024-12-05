import os
import pandas as pd
import numpy as np
import streamlit as st
# import openai

from prompts import *
from config import *
from get_data import *
import openpyxl
from functions import *

from pandasai import SmartDataframe
from pandasai.callbacks import BaseCallback
from pandasai.llm import OpenAI
from pandasai.responses.response_parser import ResponseParser


class StreamlitCallback(BaseCallback):
    def __init__(self, container) -> None:
        """Initialize callback handler."""
        self.container = container

    def on_code(self, response: str):
        self.container.code(response)


class StreamlitResponse(ResponseParser):
    def __init__(self, context) -> None:
        super().__init__(context)

    def format_dataframe(self, result):
        st.dataframe(result["value"])
        return

    def format_plot(self, result):
        st.image(result["value"])
        return

    def format_other(self, result):
        st.write(result["value"])
        return


df = get_mm_data()

#################################################### BUILD DASHBOARD ############################################

st.set_page_config(page_title=dashboard_main_title, layout="wide")
set_vertical_scrollbar_style()
set_horizontal_scrollbar_style()
st.markdown(f"<h1 style='color:{default_color1};'>{dashboard_main_title}</h1>", unsafe_allow_html=True)

st.sidebar.markdown(f'<a><img src="{travel_logo_url}" alt="Logo" style="width: 100%;"></a>', unsafe_allow_html=True)

st.markdown(mmd_str, unsafe_allow_html=True)

st.sidebar.header("Select index:")
indicator = st.sidebar.selectbox(
    "Choose an indicator to analyse:", ("Analyse data", "ModelMate GPT")
)

if indicator == "Analyse data":
    #st.markdown(f"<h6 style='color:#4CAF50;'>Raw data</h6>", unsafe_allow_html=True)

    if st.checkbox("Show the raw ModelMate data"):
        st.dataframe(df, hide_index=True)

    st.header("Filtered Data")
    st.sidebar.header("Filter Data")
    st.sidebar.write("To select all IDs select 0 in ID filter.")
    filtered_df = apply_filters(df)

    st.dataframe(filtered_df, hide_index=True)

    st.header("Filtered data overview")

    st.write(f" ")
    st.write(f"Shape of the DataFrame: {filtered_df.shape[0]} rows, {filtered_df.shape[1]} columns")

    st.markdown("#### Unique values and % of categorical columns:")

    columns_to_display = ['Detetor', 'Sponsor - Dependentes', 'Sponsor - Área Funcional',
                          'Âmbito do Modelo', 'Natureza da Medida', 'Parâmetro', 'Status de Modelo',
                          'Severidade', 'Tipo de Deadline', 'Nível de Completude', 'Status', 'Observações - Detetor',
                          'Articulação com DCIPD', 'Item Type', 'Path']

    display_dataframe_as_html_table(show_all_categorical_summary(filtered_df)[columns_to_display],  min_column_widths={
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
        'Observações - Detetor': 1500

        })

    st.write('')
    st.markdown("#### Summary statistics about numeric columns:")

    display_dataframe_as_html_table(filtered_df.describe().reset_index(names='').drop(columns=['ID']).replace({np.nan: ''}))

    st.header("Missing values")
    display_dataframe_as_html_table(null_percentage_table(filtered_df))
    #st.write(null_percentage_table(filtered_df))

    st.title('Variables distribution')

    numeric_columns = filtered_df.drop(columns=['ID']).select_dtypes(include=['float64', 'int']).columns
    column = st.selectbox('Choose the variable to plot the distribution:', numeric_columns)

    plot_distribution(df, column)

elif indicator == "ModelMate GPT":
    st.title("ModelMate GPT")

    with st.expander("🔎 Dataframe Preview"):
        st.write(df.tail(5))

    st.write(api_key)

    query = st.text_area("🗣️ Chat with Dataframe")
    container = st.container()

    if query:
        llm = OpenAI(api_token=api_key)
        query_engine = SmartDataframe(
            df,
            config={
                "llm": llm,
                "response_parser": StreamlitResponse,
                "callback": StreamlitCallback(container),
            },
        )

        try:
            answer = query_engine.chat(query)
        except Exception as e:
            st.error(f"Error: {e}")
