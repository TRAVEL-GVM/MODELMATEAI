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
 
class StreamlitCallback_v2(BaseCallback):
    def __init__(self, container, show_code=False) -> None:  # Novo parâmetro
        self.container = container
        self.show_code = show_code  # Controla se o código é exibido
 
    def on_code(self, response: str):
        if self.show_code:  # Só mostra o código se show_code=True
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
 
st.sidebar.header("STARTING MENU:")
indicator = st.sidebar.selectbox(
    "CHOOSE A SECTION:", ("Analyse data", "ModelMate GPT")
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

    # Adaptar ao tamanho da tela
    window_width = st.session_state.get('window_width', 800)  # Obter via JS ou estimar
    fig_width = min(8, window_width / 100)  # Não ultrapassar 8 polegadas
    plot_distribution_v2(df, column, width=fig_width)
 
elif indicator == "ModelMate GPT":
    # Configuração de estilo específica para o GPT
    st.markdown("""
    <style>
        .gpt-container {
            background-color: #ffffff;
            border-radius: 10px;
            padding: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        .gpt-button {
            background: linear-gradient(135deg, #6e8efb, #a777e3);
            color: white;
            border: none;
            padding: 12px 24px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            font-size: 16px;
            margin: 10px 0;
            cursor: pointer;
            border-radius: 25px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .gpt-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
            background: linear-gradient(135deg, #5e7cea, #9d68e1);
        }
        .gpt-textarea {
            border-radius: 10px;
            border: 2px solid #e0e0e0;
            padding: 15px;
            font-size: 16px;
        }
        .gpt-toggle {
            margin: 15px 0;
        }
        .gpt-response {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            border-left: 5px solid #6e8efb;
        }
    </style>
    """, unsafe_allow_html=True)

    with st.container():
       st.markdown(f"""
       <div style='text-align: center; margin-bottom: 30px;'>
           <h1 style='color: {default_color1};'>🤖 ModelMate GPT</h1>
           <p style='color: #666; font-size: 16px;'>Your AI assistant for Model Mate insights</p>
       </div>
       """, unsafe_allow_html=True)

    # Seção de visualização de dados
    with st.expander("🔍 Data preview (Random sample)", expanded=False):
        st.dataframe(df.sample(5), use_container_width=True, hide_index=True)

    show_code = st.toggle(
        "👨💻 Show code",
        help="🔧 Show Python code generated in the backend.",
        key="show_code_toggle", 
        value=False
    )

    query = st.text_area(
        "💡 Make your question about the data:",
        height=150,
        placeholder="Example: Make a bar plot of the frequency of each detector. The bars must be green.",
        help="Write your question in natural language for data analysis/querying outputs",
        key="gpt_textarea"
    )
    
    container = st.container()
    
    if st.button("Send"):
        if query:
            with st.spinner("Processing your prompt... ⏳"):
                try:
                    llm = OpenAI(api_token=st.secrets["openai"]["api_key"])
                    query_engine = SmartDataframe(
                        df,
                        config={
                            "llm": llm,
                            "response_parser": StreamlitResponse,
                            "callback": StreamlitCallback_v2(container, show_code=show_code)
                        },
                    )
                    answer = query_engine.chat(query)
                    st.toast("✅ Analysis completed successfully!", icon="✅")
                except Exception as e:
                    st.error(f"Error processing your request: {str(e)}")
                    st.markdown(f"""
                    <div class='gpt-response'>
                        <p style='color: #d32f2f;'>An error occurred while processing your question.</p>
                        <details>
                            <summary>Technical details</summary>
                            <code>{str(e)}</code>
                        </details>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Please enter your question before submitting")
