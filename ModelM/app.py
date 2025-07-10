import os
import pandas as pd
import numpy as np
import streamlit as st
from prompts import *
from config import *
from get_data import *
import openpyxl
from functions import *
from pandasai import SmartDataframe
from pandasai.callbacks import BaseCallback
from pandasai.llm import OpenAI
from pandasai.responses.response_parser import ResponseParser
import io
from datetime import datetime, timedelta
 
class StreamlitCallback(BaseCallback):
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
df['Deadline Implementação'] = pd.to_datetime(df['Deadline Implementação'], errors='coerce')
df['Data Referência Documental'] = pd.to_datetime(df['Data Referência Documental'], errors='coerce')
 
#################################################### BUILD DASHBOARD ############################################
 
st.set_page_config(page_title=dashboard_main_title, layout="wide")
set_vertical_scrollbar_style()
set_horizontal_scrollbar_style()

st.markdown(f'<a><img src="{travel_logo_url}" alt="Logo" style="width: 25%;"></a>', unsafe_allow_html=True)

st.markdown(f"<h1 style='color:{default_color1};'>{dashboard_main_title}</h1>", unsafe_allow_html=True)
 
st.markdown("""
<style>

	.stTabs [data-baseweb="tab-list"] {
		gap: 2px;
        font-size: 5rem;
    }

	.stTabs [data-baseweb="tab"] {
		height: 50px;
        width: 100%;
        white-space: pre-wrap;
		background-color: #F0F2F6;
		border-radius: 4px 4px 0px 0px;
		gap: 1px;
		padding-top: 10px;
		padding-bottom: 10px;
    }

</style>""", unsafe_allow_html=True)


# Define as abas normalmente
tab0, tab1, tab2, tab3, tab4 = st.tabs([
    "Analyse data", 
    "Model Mate GPT", 
    "Overdue and without deadline findings",
    "Upcoming findings",
    "Status monitoring"
])


with tab0:

    st.markdown(mmd_str, unsafe_allow_html=True)
 
    if st.checkbox("Show the raw ModelMate data"):
        st.dataframe(df, hide_index=True)
    
    with st.expander("Filter data 🔍", expanded=False):
        st.write("To select all IDs select 0 in ID filter.")
        filtered_df = apply_filters_v3(df)
        #st.dataframe(filtered_df, hide_index=True)
 
    with st.expander("Filtered data overview 🔍", expanded=True):

        st.write(f"Shape of the DataFrame: {filtered_df.shape[0]} rows, {filtered_df.shape[1]} columns")
    
        st.markdown("#### Unique values and % of categorical columns:")
    
        # tive que remover 'Parâmetro', 'Sponsor - Dependentes', 'Sponsor - Área Funcional'
        columns_to_display = ['Detetor',  'Status',
                            'Âmbito do Modelo', 'Natureza da Medida', 'Status de Modelo',
                            'Severidade', 'Tipo de Deadline']
    
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

with tab1:
    st.markdown(mmd_str, unsafe_allow_html=True)

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
                    llm = OpenAI(api_token=api_key)
                    query_engine = SmartDataframe(
                        df,
                        config={
                            "llm": llm,
                            "response_parser": StreamlitResponse,
                            #"callback": StreamlitCallback(container, show_code=show_code)
                        },
                    )
                    answer = query_engine.chat(query)
		    
                    st.markdown(answer)		
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

with tab2:

    min_column_widths={
            'Detetor': 100,
            'Sponsor - Área Funcional': 250,
            'Âmbito do Modelo': 130,
            'Parâmetro': 100,
            'Sponsor - Dependentes': 150, # não reconhece como categoricas não sei porquê
            'Natureza da Medida': 200,
            'Status de Modelo': 160,
            'Severidade': 170,
            'Tipo de Deadline': 170,
            'Status': 170,
            'Finding/Razão da Medida': 800,
            'Data Referência Documental': 200,
            'Referência Documental': 350,
            'ID Finding/Razão da Medida Nível 1': 250,
            'ID Obligation/Medida Nível 1': 250,
            'Obligation/Medida': 500,
            'Data de Implementação': 180,   
            'Nº de Action Items': 120,
            'Tipo Action Item - Data Quality': 140, 
            'Tipo de Deadline': 100,
            'Status': 100,
            'Observações': 500,
            'Severidade': 120,
            'Action Plan': 250,
             }
    st.markdown(mmd_str, unsafe_allow_html=True)

    hoje = datetime.now().date() 
    limit_sixty = hoje + timedelta(days=60)

    df_filtrado_open = df[(df['Deadline Implementação'].isna()) & (df['Status'].isin(['Em Curso',
                                                                                    'Reaberto']))]

    with st.expander("🔍 Findings without deadline", expanded=False):
        st.write(" Nr of findings without deadline: ", df_filtrado_open.shape[0])
        #st.dataframe(df_filtrado_open, hide_index=True)

        heightx = min(df_filtrado_open.shape[0]*130, 800)

        display_dataframe_with_scroll(df_filtrado_open, min_column_widths=min_column_widths, height=heightx)

    with st.expander("🔍 Findings overdue as of today", expanded=False):

        df_overdue = df[(df['Deadline Implementação'] <= str(hoje)) 
                                      & (df['Status'].isin(['Em Curso', 'Reaberto']))]
        
        st.write(" Nr of findings without deadline: ", df_overdue.shape[0])
        if df_overdue.empty:
            st.write("No overdue findings without deadline.")
        else:
            #st.dataframe(df_overdue, hide_index=True)
            heighty = min(df_overdue.shape[0]*130, 800)

            display_dataframe_with_scroll(df_overdue, min_column_widths=min_column_widths, height=heighty)

    with st.expander("🔍 Findings in overdue up to 3 months", expanded=False):
        
        df_overdue_3m = df[(df['Deadline Implementação'] >= str(hoje - timedelta(days=90)))
                            & (df['Deadline Implementação'] <= str(hoje))
                            & (df['Status'].isin(['Em Curso', 'Reaberto']))]
        
        st.write(" Nr of findings without deadline: ", df_overdue_3m.shape[0])
        if df_overdue_3m.empty:
            st.write("No overdue findings without deadline.")
        else:
            #st.dataframe(df_overdue_3m, hide_index=True)
            heightz = min(df_overdue_3m.shape[0]*130, 800)

            display_dataframe_with_scroll(df_overdue_3m, min_column_widths=min_column_widths, height=heightz)

    with st.expander("🔍 Findings in overdue up to 6 months", expanded=False):
        df_overdue_36m = df[(df['Deadline Implementação'] >= str(hoje - timedelta(days=180))) & 
                            (df['Deadline Implementação'] < str(hoje - timedelta(days=90)))
                            & (df['Status'].isin(['Em Curso', 'Reaberto']))]
        
        st.write(" Nr of findings without deadline: ", df_overdue_36m.shape[0])
        if df_overdue_36m.empty:
            st.write("No overdue findings without deadline.")
        else:
            #st.dataframe(df_overdue_36m, hide_index=True)
            heightb = min(df_overdue_36m.shape[0]*150, 1000)

            display_dataframe_with_scroll(df_overdue_36m, min_column_widths=min_column_widths, height=heightb)
    
    with st.expander("🔍 Findings in overdue for more than 6 months", expanded=False):
        st.write(str(hoje - timedelta(days=180)))
        df_overdue_6m = df[(df['Deadline Implementação'] < str(hoje - timedelta(days=180)))
                            & (df['Status'].isin(['Em Curso', 'Reaberto']))]
        
        st.write(" Nr of findings without deadline: ", df_overdue_6m.shape[0])
        if df_overdue_6m.empty:
            st.write("No overdue findings without deadline.")
        else:
            heighta = min(df_overdue_6m.shape[0]*150, 1000)

            display_dataframe_with_scroll(df_overdue_6m, min_column_widths=min_column_widths, height=heighta)
            #st.dataframe(df_overdue_6m, hide_index=True)

with tab3:
    st.header("Upcoming findings")

    df_upcoming = df[  (df['Deadline Implementação'] >= str(hoje)) 
                     & (df['Deadline Implementação'] <= str(hoje + timedelta(days=60))) 
                     & (df['Status'].isin(['Em Curso', 'Reaberto'])) 
                     & (df['Deadline Implementação'].notna())]

    st.write("Nr of upcoming findings: ", df_upcoming.shape[0])
    #st.write(df_upcoming)
    display_dataframe_with_scroll(df_upcoming, min_column_widths=min_column_widths, height=800)


with tab4:
    st.header("...")

    #dfx = pd.read_excel(nmd_old_path)
    #st.write(dfx)
