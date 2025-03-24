import os
import pandas as pd
import numpy as np
import streamlit as st
from pandasai import SmartDataframe
from pandasai.callbacks import BaseCallback
from pandasai.llm import OpenAI
from pandasai.responses.response_parser import ResponseParser

# Configurações de estilo
def setup_styles():
    st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            border: none;
        }
        .stButton>button:hover {
            background-color: #45a049;
        }
        .stTextArea textarea {
            border-radius: 5px;
            border: 1px solid #ced4da;
        }
        .stExpander {
            border-radius: 5px;
            border: 1px solid #e9ecef;
        }
        .stDataFrame {
            border-radius: 5px;
        }
        .css-1aumxhk {
            background-color: #ffffff;
            border-radius: 5px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1, h2, h3, h4, h5, h6 {
            color: #2c3e50;
        }
    </style>
    """, unsafe_allow_html=True)

class StreamlitCallback(BaseCallback):
    def __init__(self, container=None, show_code=False) -> None:
        self.container = container or st.container()
        self.show_code = show_code

    def on_code(self, response: str):
        if self.show_code:
            with self.container:
                st.markdown("### Generated Python Code")
                st.code(response, language='python')

class StreamlitResponse(ResponseParser):
    def __init__(self, context=None) -> None:
        super().__init__(context)

    def format(self, output):
        if output["type"] == "dataframe":
            st.dataframe(output["value"], use_container_width=True)
        elif output["type"] == "plot":
            st.image(output["value"], use_container_width=True)
        else:
            st.markdown(f"""
            <div style="background-color: #f0f2f6; 
                        padding: 15px; 
                        border-radius: 5px; 
                        margin: 10px 0;">
                {output["value"]}
            </div>
            """, unsafe_allow_html=True)

# Configuração inicial
setup_styles()
df = get_mm_data()

# Layout principal
st.set_page_config(page_title=dashboard_main_title, layout="wide", page_icon="📊")

# Barra lateral
with st.sidebar:
    st.image(travel_logo_url, use_column_width=True)
    st.markdown(f"<h2 style='text-align: center; color: {default_color1};'>{dashboard_main_title}</h2>", 
                unsafe_allow_html=True)
    indicator = st.radio(
        "Navigation",
        ["Analyze Data", "ModelMate GPT"],
        index=0,
        label_visibility="collapsed"
    )

# Conteúdo principal
st.markdown(mmd_str, unsafe_allow_html=True)

if indicator == "Analyze Data":
    st.header("📈 Data Analysis Dashboard")
    
    with st.expander("🔍 Raw Data Preview", expanded=False):
        if st.checkbox("Show complete dataset"):
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.dataframe(df.head(), use_container_width=True, hide_index=True)
    
    st.subheader("🔎 Data Exploration")
    
    with st.container():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("### Filters")
            filtered_df = apply_filters(df)
        with col2:
            st.markdown("### Filtered Data")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    with st.expander("📊 Data Statistics", expanded=True):
        tab1, tab2, tab3 = st.tabs(["Categorical Analysis", "Numerical Analysis", "Missing Values"])
        
        with tab1:
            columns_to_display = ['Detetor', 'Âmbito do Modelo', 'Natureza da Medida', 
                                 'Status de Modelo', 'Severidade', 'Tipo de Deadline', 
                                 'Status', 'Item Type', 'Path']
            st.dataframe(
                show_all_categorical_summary(filtered_df)[columns_to_display],
                use_container_width=True,
                height=400
            )
        
        with tab2:
            desc_df = filtered_df.describe()
            sum_row = filtered_df.sum(numeric_only=True).rename('sum')
            desc_with_sum = desc_df.append(sum_row)
            num_statistics_df = (desc_with_sum
                        .reset_index(names='')
                        .drop(columns=['ID'], errors='ignore')  
                        .replace({np.nan: ''})
                        .applymap(format_number))
            st.dataframe(num_statistics_df, use_container_width=True)
        
        with tab3:
            st.dataframe(
                null_percentage_table(filtered_df),
                use_container_width=True
            )
    
    st.subheader("📉 Data Visualization")
    numeric_columns = filtered_df.drop(columns=['ID']).select_dtypes(include=['float64', 'int']).columns
    selected_column = st.selectbox('Select variable for distribution plot:', numeric_columns)
    plot_distribution(filtered_df, selected_column)

elif indicator == "ModelMate GPT":
    st.header("🤖 ModelMate GPT Assistant")
    
    with st.expander("📂 Data Preview", expanded=False):
        st.dataframe(df.sample(5), use_container_width=True, hide_index=True)
    
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            query = st.text_area(
                "Enter your question about the data:",
                height=150,
                placeholder="E.g.: What is the distribution of detectors?",
                help="Ask natural language questions about your data"
            )
        with col2:
            st.write("")  # Spacer
            st.write("")
            show_code = st.toggle("Show generated code", help="Display the Python code used to generate the answer")
    
    if st.button("Analyze", type="primary"):
        if query:
            with st.spinner("Analyzing your question..."):
                try:
                    container = st.container()
                    
                    llm = OpenAI(api_token=st.secrets["openai"]["api_key"])
                    query_engine = SmartDataframe(
                        df,
                        config={
                            "llm": llm,
                            "response_parser": StreamlitResponse(container),
                            "callback": StreamlitCallback(container, show_code=show_code),
                            "save_charts": True,
                            "save_charts_path": "temp_charts"
                        },
                    )
                    
                    os.makedirs("temp_charts", exist_ok=True)
                    for file in glob.glob("temp_charts/*.png"):
                        os.remove(file)
                    
                    response = query_engine.chat(query)
                    
                    if os.path.exists("temp_charts/temp_chart.png"):
                        st.image("temp_charts/temp_chart.png", use_container_width=True)
                    
                    st.success("Analysis completed!")
                
                except Exception as e:
                    st.error(f"Error processing your request: {str(e)}")
        else:
            st.warning("Please enter a question to analyze")
