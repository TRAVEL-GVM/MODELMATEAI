import streamlit as st
import pandas as pd
import numpy as np


def show_all_categorical_summary(df):
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns

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
        font-size: 11px;  /* Smaller font size */
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
            css += f"th:nth-child({df.columns.get_loc(col) + 1}), td:nth-child({df.columns.get_loc(col) + 1}) {{ min-width: {width}px; }}\n"

    css += "</style>\n"

    # Combine CSS and HTML table
    full_html = css + html_table

    # Display in Streamlit
    st.markdown(full_html, unsafe_allow_html=True)