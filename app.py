"""
Data Visualizer Streamlit App - Main Entry Point

This is the main entry point for the data visualization Streamlit app.
Sets up the layout, routing, and coordinates between different components.
"""

import streamlit as st
import pandas as pd
from components.sidebar import render_sidebar
from components.charts import render_charts
from utils.file_loader import load_data
from style import apply_global_style


def main():
    """
    Main application entry point.
    Sets up the Streamlit page configuration and renders the UI.
    """
    # Configure page
    st.set_page_config(
        page_title="Data Visualizer",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply global styling
    apply_global_style()

    # Main title
    st.title("📊 Data Visualizer")
    st.markdown("Upload your CSV or Excel file to get instant data insights!")

    # Render sidebar for file upload and options
    uploaded_file, options = render_sidebar()

    # Main content area
    if uploaded_file is not None:
        try:
            # Load and cache the data
            df = load_data(uploaded_file)

            # Display basic info
            st.subheader("Dataset Overview")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric(
                    "Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB")

            # Render charts based on selected options
            render_charts(df, options)

        except Exception as e:
            st.error(f"Error loading data: {str(e)}")
    else:
        st.info("👆 Please upload a CSV or Excel file to get started!")


if __name__ == "__main__":
    main()
