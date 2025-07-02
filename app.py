"""
Data Visualizer Streamlit App - Main Entry Point

A streamlined data visualization tool with tab-based interface for easy data exploration.
Features separate tabs for data overview, missing values, distributions, correlations, and categorical analysis.
Clean, focused UI without unnecessary sidebar options.
"""

import streamlit as st
import pandas as pd
from utils.file_loader import load_data
from style import apply_global_style

# Import tab modules
from components.data_overview import render_data_overview_tab
from components.missing_values import render_missing_values_tab
from components.distributions import render_distributions_tab
from components.correlations import render_correlations_tab
from components.categorical import render_categorical_tab
from components.color_settings import render_color_palette_settings, apply_palette_to_session


def render_file_uploader():
    """Render the file upload section."""
    st.sidebar.title("📊 Data Visualizer")
    st.sidebar.markdown("---")

    # File uploader
    st.sidebar.subheader("📁 Upload Your Data")
    uploaded_file = st.sidebar.file_uploader(
        "Choose a CSV or Excel file",
        type=['csv', 'xlsx', 'xls'],
        help="Upload a CSV or Excel file to analyze"
    )

    # Show file info if uploaded
    if uploaded_file is not None:
        file_details = {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB"
        }
        st.sidebar.success("✅ File uploaded successfully!")
        for key, value in file_details.items():
            st.sidebar.text(f"{key}: {value}")

    st.sidebar.markdown("---")

    # Color palette settings
    selected_palette = render_color_palette_settings()
    apply_palette_to_session(selected_palette)

    return uploaded_file


def render_dataset_metrics(df):
    """Render basic dataset metrics."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📊 Rows", f"{len(df):,}")
    with col2:
        st.metric("📋 Columns", len(df.columns))
    with col3:
        st.metric(
            "💾 Memory", f"{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    with col4:
        missing_count = df.isnull().sum().sum()
        st.metric("❓ Missing Values", f"{missing_count:,}")


def main():
    """Main application entry point."""
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

    # File upload
    uploaded_file = render_file_uploader()

    if uploaded_file is not None:
        try:
            # Load and cache the data
            df = load_data(uploaded_file)

            # Display basic metrics
            render_dataset_metrics(df)

            st.markdown("---")

            # Create tabs for different analysis types
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📋 Data Overview",
                "❓ Missing Values",
                "📊 Distributions",
                "🔗 Correlations",
                "📂 Categories"
            ])

            with tab1:
                render_data_overview_tab(df)

            with tab2:
                render_missing_values_tab(df)

            with tab3:
                render_distributions_tab(df)

            with tab4:
                render_correlations_tab(df)

            with tab5:
                render_categorical_tab(df)

        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
            st.info("💡 Please check your file format and try again.")
    else:
        # Show getting started information
        st.info("👆 Please upload a CSV or Excel file to get started!")

        # Show sample data information
        with st.expander("💡 Try with Sample Data", expanded=True):
            st.markdown("""
            **Sample datasets are available in the `sample_data/` folder:**
            
            - 📈 **sales_data.csv** - E-commerce sales data with mixed types
            - 🎓 **student_performance.csv** - Academic performance with correlations  
            - 🔧 **messy_data.csv** - Dataset with missing values for testing
            - 💳 **high_cardinality_data.csv** - Transaction data with many categories
            
            **Supported formats:** CSV, Excel (.xlsx, .xls)
            """)


if __name__ == "__main__":
    main()
