"""
Vizzy Streamlit App - Main Entry Point

A streamlined data visualization tool with tab-based interface for easy data exploration.
Features separate tabs for data overview, missing values, distributions, correlations, and categorical analysis.
Clean, focused UI without unnecessary sidebar options.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from utils.file_loader import load_data
from utils.pdf_report import generate_pdf_report
from style import apply_global_style

# Import tab modules
from components.data_overview import render_data_overview_tab
from components.missing_values import render_missing_values_tab
from components.distributions import render_distributions_tab
from components.correlations import render_correlations_tab
from components.categorical import render_categorical_tab
from components.time_series import render_time_series_tab
from components.preprocessing import render_preprocessing_tab
from components.color_settings import render_color_palette_settings, apply_palette_to_session


def render_file_uploader():
    """Render the file upload section."""
    st.sidebar.title("📊 Vizzy")
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


def render_pdf_export_section(df, uploaded_file=None):
    """Render PDF export functionality."""
    st.sidebar.markdown("---")
    st.sidebar.subheader("📄 Export Report")

    # Development status warning
    st.sidebar.warning(
        "⚠️ **Under Development**\n\nPDF export is currently in beta. The generated report includes basic analysis but may need formatting improvements.")

    if st.sidebar.button("📊 Generate PDF Report (Beta)", type="secondary", use_container_width=True):
        with st.sidebar.spinner("Generating basic PDF report..."):
            try:
                # Get dataset name from uploaded file
                dataset_name = uploaded_file.name if uploaded_file else "Sample Dataset"

                # Generate the PDF report
                pdf_bytes = generate_pdf_report(df, dataset_name=dataset_name)

                # Create download button
                filename = f"vizzy_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                st.sidebar.download_button(
                    label="💾 Download PDF Report",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                st.sidebar.success(
                    "✅ Basic PDF report generated successfully!")
                st.sidebar.info(
                    "💡 This is a beta feature. Future versions will include charts and enhanced formatting.")

            except Exception as e:
                st.sidebar.error(f"❌ Error generating PDF: {str(e)}")
                st.sidebar.error(
                    "Please try again or contact support if the issue persists.")


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
        page_title="Vizzy",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Apply global styling
    apply_global_style()

    # Main title
    st.title("📊 Vizzy")
    st.markdown("Upload your CSV or Excel file to get instant data insights!")

    # File upload
    uploaded_file = render_file_uploader()

    if uploaded_file is not None:
        try:
            # Load and cache the data
            df = load_data(uploaded_file)

            # Display basic metrics
            render_dataset_metrics(df)

            # Add PDF export functionality to sidebar
            render_pdf_export_section(df, uploaded_file)

            st.markdown("---")

            # Create tabs for different analysis types
            tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
                "📋 Data Overview",
                "❓ Missing Values",
                "📊 Distributions",
                "🔗 Correlations",
                "📂 Categories",
                "📈 Time Series",
                "🛠️ Preprocessing"
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

            with tab6:
                render_time_series_tab(df)

            with tab7:
                render_preprocessing_tab(df)

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
