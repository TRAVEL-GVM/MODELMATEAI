import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import *
from io import StringIO


def show_all_categorical_summary(df):
    categorical_columns = list(df.select_dtypes(include=['object', 'category']).columns)

    summary_dict = {}

    max_unique_count = max(df[col].nunique() for col in categorical_columns if df[col].nunique() <= 10)

    for col in categorical_columns:
        if df[col].nunique() > 10:
            continue

        value_counts = df[col].value_counts(normalize=True) * 100

        summary = [f'{val} - {np.round(perc, 2)}%' for val, perc in zip(value_counts.index, value_counts.values)]

        summary.extend([np.nan] * (max_unique_count - len(summary)))

        summary_dict[col] = summary

    final_summary = pd.DataFrame(summary_dict)
    final_summary = final_summary.dropna(how='all')
    final_summary.name = 'Unique - %'
    final_summary = final_summary.replace({np.nan: ''})

    return final_summary


def display_dataframe_as_html_table(df, min_column_widths=None):
    """
    Display DataFrame as HTML table in Streamlit with centered text and green header.

    :param df: DataFrame to display
    :param min_column_widths: Optional dictionary of {column_name: min_width_in_px}
    """
    # Generate HTML table
    html_table = df.to_html(index=False, escape=True)

    # CSS for styling
    css = """
    <style>
    table { 
        border-collapse: collapse; 
        width: 100%; 
        font-size: 15px;  /* Smaller font size */
    }
    th {
        background-color: #179297;  /* Green background for header */
        color: white;
        text-align: center;  /* Center-align header */
    }
    td { 
        border: 1px solid #ddd; 
        padding: 8px; 
        text-align: left;  /* Align data cells to the left */
    }
    """

    # Add custom column width CSS if specified
    if min_column_widths:
        for col, width in min_column_widths.items():
            if col in df.columns:
                # Applies the custom width only if the column exists
                css += f"th:nth-child({df.columns.get_loc(col) + 1}), td:nth-child({df.columns.get_loc(col) + 1}) {{ min-width: {width}px; }}\n"
            else:
                st.warning(f"Coluna {col} não encontrada no DataFrame")

    css += "</style>\n"

    # Combine CSS and HTML table
    full_html = css + html_table

    # Display in Streamlit
    st.markdown(full_html, unsafe_allow_html=True)



def plot_distribution(df, column_name):
    """
    Gera um gráfico de distribuição para a variável selecionada do DataFrame.

    :param df: DataFrame com os dados.
    :param column_name: Nome da coluna para a qual será gerado o gráfico de distribuição.
    """

    numeric_columns = df.select_dtypes(include=['float64', 'int']).columns
    if column_name in numeric_columns:

        sns.set(style="whitegrid")

        plt.figure(figsize=(4, 2))
        sns.histplot(df[column_name], kde=True, bins=20, color=default_color1)
        plt.title(f'{column_name} distribution', size=8, color=default_color1)
        plt.xlabel(column_name, size=6)
        plt.ylabel('Frequency', size=6)
        plt.tick_params(axis='both', which='major', labelsize=6)

        st.pyplot(plt)

        plt.clf()
    else:
        st.error(f"Column '{column_name}' does not exist in ModelMate.")


def null_percentage_table(df):
    """
    Retorna uma tabela com a porcentagem de valores nulos por coluna.

    :param df: DataFrame a ser analisado
    :return: DataFrame com a porcentagem de valores nulos por coluna
    """

    null_percentages = round(df.isnull().mean() * 100, 2)

    null_table = pd.DataFrame({
        'Column': null_percentages.index,
        'Null Percentage (%)': null_percentages.values
    })

    null_table = null_table.sort_values(by='Null Percentage (%)', ascending=False).reset_index(drop=True).T
    null_table.columns = null_table.iloc[0, :]
    null_table = null_table.iloc[1:, :]

    return null_table


def apply_filters(df):
    st.sidebar.header("Filters")

    filtered_df1 = df.copy()  # Evita modificar o DataFrame original diretamente
    categorical_columns = ['Status', 'Âmbito do Modelo', 'Segmento', 'Severidade', 'Detetor', 'Sponsor',
                           'ID Finding/Razão da Medida Nível 1', 'ID Obligation/Medida Nível 1']

    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype(str)  # Converte a coluna para string
        else:
            st.warning(f"Coluna {col} não encontrada no DataFrame")

    # Verifica se a coluna 'ID' existe antes de filtrar
    id_column = [col for col in df.columns if col.lower() == 'id']
    if id_column:
        id_column = id_column[0]
        id_filter = st.sidebar.number_input('Filter by ID', min_value=0)
        
        # Aplica o filtro de ID apenas se o valor for maior que 0
        if id_filter > 0:
            filtered_df1 = filtered_df1[filtered_df1[id_column] == id_filter]

    # Aplicar filtros para colunas categóricas
    for col in categorical_columns:
        if col in df.columns:
            unique_values = sorted(df[col].unique())
            selected_values = st.sidebar.multiselect(
                f'Select {col}',
                unique_values,
                default=[]
            )

            if selected_values:
                filtered_df1 = filtered_df1[filtered_df1[col].isin(selected_values)]
        else:
            st.warning(f"Coluna {col} não encontrada no DataFrame")

    return filtered_df1


def apply_filters_v3(df):
    st.header("Filters")

    filtered_df1 = df.copy()  # Evita modificar o DataFrame original diretamente
    categorical_columns = ['Status', 'Âmbito do Modelo', 'Segmento', 'Severidade', 'Detetor', 'Sponsor',
                           'ID Finding/Razão da Medida Nível 1', 'ID Obligation/Medida Nível 1']

    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype(str)  # Converte a coluna para string
        else:
            st.warning(f"Coluna {col} não encontrada no DataFrame")

    col1, col2 = st.columns([1, 4])

    with col1:
        # Verifica se a coluna 'ID' existe antes de filtrar
        id_column = [col for col in df.columns if col.lower() == 'id']
        if id_column:
            id_column = id_column[0]
            id_filter = st.number_input('Filter by ID', min_value=0)
            
            # Aplica o filtro de ID apenas se o valor for maior que 0
            if id_filter > 0:
                filtered_df1 = filtered_df1[filtered_df1[id_column] == id_filter]

        # Aplicar filtros para colunas categóricas
        for col in categorical_columns:
            if col in df.columns:
                unique_values = sorted(df[col].unique())
                selected_values = st.multiselect(
                    f'Select {col}',
                    unique_values,
                    default=[]
                )

                if selected_values:
                    filtered_df1 = filtered_df1[filtered_df1[col].isin(selected_values)]
    with col2:
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
            'ID Finding/Razão da Medida Nível 1': 250,
            'ID Obligation/Medida Nível 1': 250,
            'Obligation/Medida': 500,
            'Data de Implementação': 180,   
            'Nº de Action Items': 120,
            'Tipo Action Item - Data Quality': 140, 
            'Tipo de Deadline': 100,
            'Status': 100,
            'Observações': 300,
            'Severidade': 120,
            'Action Plan': 250,
                              }

        display_dataframe_with_scroll(filtered_df1, min_column_widths=min_column_widths, height=800)
        #st.dataframe(filtered_df1, use_container_width=True)

    return filtered_df1


def apply_filters_v2(df):
    filtered_df = df.copy()
    
    # Lista de colunas categóricas para filtrar
    categorical_columns = ['Status', 'Âmbito do Modelo', 'Segmento', 'Severidade', 'Detetor', 'Sponsor',
                         'ID Finding/Razão da Medida Nível 1', 'ID Obligation/Medida Nível 1']
    
    # Converter colunas categóricas para string
    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype(str)
        else:
            st.warning(f"Coluna {col} não encontrada no DataFrame")

    # Criar colunas para os filtros
    cols = st.columns(9)  # 3 colunas (ajuste conforme necessário)
    
    # Filtro de ID (na primeira coluna)
    with cols[0]:
        id_column = [col for col in df.columns if col.lower() == 'id']
        if id_column:
            id_column = id_column[0]
            id_filter = st.number_input('Filter by ID (0 = all)', min_value=0)
            if id_filter > 0:
                filtered_df = filtered_df[filtered_df[id_column] == id_filter]
    
    # Filtros categóricos (distribuídos pelas colunas)
    for i, col in enumerate(categorical_columns):
        if col in df.columns:
            with cols[(i % len(cols))]:  # Distribui entre as colunas
                unique_values = sorted(df[col].unique())
                selected_values = st.multiselect(
                    f'Select {col}',
                    unique_values,
                    default=[]
                )
                if selected_values:
                    filtered_df = filtered_df[filtered_df[col].isin(selected_values)]
    
    return filtered_df



def display_dataframe_as_html_table_v2(df, min_column_widths=None, row_height=20):
    """
    Display DataFrame as HTML table in Streamlit with centered text, green header,
    fixed row height, and horizontal scrolling.

    :param df: DataFrame to display
    :param min_column_widths: Optional dictionary of {column_name: min_width_in_px}
    :param row_height: Height of each row in pixels (default is 20px)
    """
    # Generate HTML table
    html_table = df.to_html(index=False, escape=True)

    # CSS for styling with horizontal scrolling
    css = f"""
    <style>
    .table-container {{
        overflow-x: auto;  /* Enable horizontal scrolling */
        width: 100%;
    }}
    table {{
        border-collapse: collapse;
        width: max-content;  /* Allow table to expand beyond container */
        min-width: 100%;
        font-size: 11px;
    }}
    th {{
        background-color: #179297;
        color: white;
        text-align: center;
        position: sticky;  /* Optional: make header sticky */
        top: 0;
        z-index: 1;
    }}
    td {{
        border: 1px solid #ddd;
        padding: 8px;
        text-align: left;
        height: {row_height}px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}
    """

    # Add custom column width CSS if specified
    if min_column_widths:
        for col, width in min_column_widths.items():
            css += f"th:nth-child({df.columns.get_loc(col) + 1}), td:nth-child({df.columns.get_loc(col) + 1}) {{ min-width: {width}px; }}\n"

    css += "</style>\n"

    # Wrap table in a scrollable container
    full_html = f"""
    {css}
    <div class="table-container">
    {html_table}
    </div>
    """

    # Display in Streamlit
    st.markdown(full_html, unsafe_allow_html=True)


def set_vertical_scrollbar_style():
    st.markdown(
        """
        <style>
        /* CSS para personalizar a barra de rolagem */
        ::-webkit-scrollbar {
            width: 10px;
        }

        ::-webkit-scrollbar-track {
            background: #179297;
        }

        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def set_horizontal_scrollbar_style():
    st.markdown(
        """
        <style>
        /* CSS para personalizar a barra de rolagem horizontal */
        ::-webkit-scrollbar {
            height: 12px;
        }

        ::-webkit-scrollbar-track {
            background: #179297;
        }

        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 10px;
        }

        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def format_number(x):
    if isinstance(x, (int, float)):
        return f"{x:.2f}".rstrip('0').rstrip('.')
    return x



def plot_distribution_v2(df, column_name, width=6):
    """
    Args:
        width: Largura desejada em polegadas (padrão: 6")
    """
    # Calcular altura proporcional
    height = width * 0.5  # Proporção 2:1 (largura:altura)
    
    fig, ax = plt.subplots(figsize=(width, height))
    sns.histplot(data=df, x=column_name, kde=True, ax=ax, color=default_color1)
    
    # Ajustes estéticos
    plt.title(f"Distribuição de {column_name}", pad=10)
    plt.tight_layout()
    
    # Container para controle preciso
    with st.container():
        st.pyplot(fig, use_container_width=False)
    plt.close(fig)


def display_dataframe_with_scroll(df, min_column_widths=None, height=800):
    """
    Display DataFrame as HTML table in Streamlit with scroll bars, centered text and green header.

    :param df: DataFrame to display
    :param min_column_widths: Optional dictionary of {column_name: min_width_in_px}
    :param height: Height of the table container in pixels (default: 800)
    """
    # Generate HTML table
    html_table = df.to_html(index=False, escape=True, classes="dataframe-table")

    # CSS for styling
    css = f"""
    <style>
    .dataframe-container {{
        height: {height}px;
        overflow: auto;
        margin: 1rem 0;
        border: 1px solid #ddd;
        border-radius: 2px;
    }}
    
    .dataframe-table {{
        border-collapse: collapse; 
        width: 100%; 
        font-size: 13px;
    }}
    
    .dataframe-table th {{
        background-color: #179297;  /* Green background for header */
        color: white;
        text-align: center;
        position: sticky;
        top: 0;
        border: 1px solid #ddd;
        padding: 5px;
    }}
    
    .dataframe-table td {{ 
        border: 1px solid #ddd; 
        padding: 8px; 
        text-align: left;
        vertical-align: top;
    }}
    
    .dataframe-table tr:nth-child(even) {{
        background-color: #f2f2f2;
    }}
    
    /* Thin scrollbars */
    .dataframe-container::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}
    
    .dataframe-container::-webkit-scrollbar-track {{
        background: #f1f1f1;
    }}
    
    .dataframe-container::-webkit-scrollbar-thumb {{
        background: #179297;
        border-radius: 3px;
    }}
    
    .dataframe-container::-webkit-scrollbar-thumb:hover {{
        background: #555;
    }}
    """

    # Add custom column width CSS if specified
    if min_column_widths:
        for col, width in min_column_widths.items():
            if col in df.columns:
                # Applies the custom width only if the column exists
                css += f".dataframe-table th:nth-child({df.columns.get_loc(col) + 1}), .dataframe-table td:nth-child({df.columns.get_loc(col) + 1}) {{ min-width: {width}px; }}\n"
            else:
                st.warning(f"Coluna '{col}' não encontrada no DataFrame")

    css += "</style>\n"

    # Combine CSS and HTML table in a scrollable container
    full_html = css + f'<div class="dataframe-container">{html_table}</div>'

    # Display in Streamlit
    st.markdown(full_html, unsafe_allow_html=True)

