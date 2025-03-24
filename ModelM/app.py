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


class CodeStorageCallback(BaseCallback):
    """Armazena o código gerado sem interferir na saída principal"""
    def __init__(self):
        self.code = None
    
    def on_code(self, response: str):
        self.code = response
        st.session_state.last_code = response  # Guarda na sessão

class CleanResponse(ResponseParser):
    """Exibe os resultados de forma limpa"""
    def format(self, output):
        if output["type"] == "dataframe":
            st.dataframe(output["value"], use_container_width=True)
        elif output["type"] == "plot":
            st.image(output["value"])
        else:
            st.markdown(f"**Resposta:**\n\n{output['value']}")


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

    # tive que remover 'Parâmetro', 'Sponsor - Dependentes', 'Sponsor - Área Funcional'
    columns_to_display = ['Detetor', 
                          'Âmbito do Modelo', 'Natureza da Medida', 'Status de Modelo',
                          'Severidade', 'Tipo de Deadline', 'Status', 'Item Type', 'Path']

    #st.dataframe(show_all_categorical_summary(filtered_df)[columns_to_display])  
    display_dataframe_as_html_table(show_all_categorical_summary(filtered_df)[columns_to_display],  min_column_widths={
        'Detetor': 140,
         #'Sponsor - Área Funcional': 300,
        'Âmbito do Modelo': 130,
         #'Parâmetro': 100,
         # 'Sponsor - Dependentes': 150, # não reconhece como categoricas não sei porquê
        'Natureza da Medida': 220,
        'Status de Modelo': 250,
        'Severidade': 170,
        'Tipo de Deadline': 170,
        'Status': 170
        })
    
    st.write('')
    st.markdown("#### Summary statistics about numeric columns:")

    desc_df = filtered_df.describe()
    sum_row = filtered_df.sum(numeric_only=True).rename('sum')
    desc_with_sum = desc_df.append(sum_row)
    
    num_statistics_df = (desc_with_sum
                .reset_index(names='')
                .drop(columns=['ID'], errors='ignore')  
                .replace({np.nan: ''})
                   .applymap(format_number))

    display_dataframe_as_html_table(num_statistics_df, min_column_widths={
        'Nº de Extensions': 100,
        'Nº de Action Items': 100,
        'Tipo Action Item - Data Quality': 120,
        'Tipo Action Item - Processos/RWA': 130,
        'Tipo Action Item - Metodologia/Documentação': 130
        })
                                   
                    

    st.header("Missing values")
    display_dataframe_as_html_table(null_percentage_table(filtered_df),
                                   min_column_widths={'Action Plan': 100,
                                                      'Limitation/Correcção': 100,
                                                      'Recommendations/Recomendações': 100,
                                                      'Sponsor - Área Funcional': 100
                                                     }
                                       )
    
    #st.write(null_percentage_table(filtered_df))

    st.title('Variables distribution')

    numeric_columns = filtered_df.drop(columns=['ID']).select_dtypes(include=['float64', 'int']).columns
    column = st.selectbox('Choose the variable to plot the distribution:', numeric_columns)

    plot_distribution(df, column)

elif indicator == "ModelMate GPT":
    st.title("ModelMate GPT")

    # Inicializa variáveis de sessão
if 'last_code' not in st.session_state:
    st.session_state.last_code = None
if 'last_result' not in st.session_state:
    st.session_state.last_result = None

# ================================================
# 3️⃣ INTERFACE PRINCIPAL
# ================================================
tab1, tab2 = st.tabs(["🔍 Consulta", "⚙️ Configurações"])

with tab1:
    with st.expander("📂 Visualização rápida dos dados"):
        st.dataframe(df.head(3), hide_index=True, use_container_width=True)

    # Área de consulta
    user_query = st.text_area("💬 Digite sua pergunta sobre os dados:", height=100)
    
    if st.button("🚀 Executar análise", type="primary"):
        if user_query:
            with st.spinner("Processando..."):
                try:
                    callback = CodeStorageCallback()
                    
                    llm = OpenAI(api_token=st.secrets["openai"]["api_key"])
                    query_engine = SmartDataframe(
                        df,
                        config={
                            "llm": llm,
                            "response_parser": CleanResponse,
                            "callback": callback,
                            "verbose": False,
                        },
                    )
                    
                    result = query_engine.chat(user_query)
                    st.session_state.last_result = result
                    st.toast("✅ Análise concluída!", icon="✅")
                    
                except Exception as e:
                    st.error(f"Erro na análise: {str(e)}")

# Seção de resultados (SEMPRE visível)
if st.session_state.last_result:
    st.divider()
    st.subheader("📝 Resultados da Análise")
    if isinstance(st.session_state.last_result, pd.DataFrame):
        st.dataframe(st.session_state.last_result, use_container_width=True)
    else:
        st.markdown(st.session_state.last_result)

# Seção de código (OPCIONAL)
if st.session_state.last_code:
    st.divider()
    with st.expander("👨💻 Código Python gerado (Clique para expandir)", expanded=False):
        st.code(st.session_state.last_code, language="python")

with tab2:
st.markdown("### Configurações avançadas")
debug_mode = st.checkbox("Modo desenvolvedor (mostrar metadados técnicos)")

if debug_mode and st.session_state.last_code:
    st.json({
        "query": user_query,
        "code_size": f"{len(st.session_state.last_code)} bytes",
        "pandasai_version": st.__version__
    })
