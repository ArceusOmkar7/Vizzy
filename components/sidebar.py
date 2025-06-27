"""
Sidebar component for file upload and visualization options.

Provides the main interface for users to upload files and select visualization types.
"""

import streamlit as st
from typing import Tuple, Dict, Any


def render_sidebar() -> Tuple[Any, Dict[str, Any]]:
    """
    Render the sidebar with file uploader and visualization options.

    Returns:
        tuple: (uploaded_file, options_dict)
    """
    st.sidebar.title("📊 Data Visualizer")
    st.sidebar.markdown("---")

    # File uploader section
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

    # Visualization options
    st.sidebar.subheader("🎯 Visualization Options")

    # Data overview options
    st.sidebar.markdown("**📋 Data Overview**")
    show_summary = st.sidebar.checkbox("Show Data Summary", value=True,
                                       help="Display basic statistics and data types")
    show_memory_usage = st.sidebar.checkbox("Show Memory Usage", value=False,
                                            help="Display memory usage by column")

    # Null analysis options
    st.sidebar.markdown("**🔍 Missing Values Analysis**")
    show_null_bar = st.sidebar.checkbox("Show Null Bar Chart", value=True,
                                        help="Bar chart showing missing values per column")
    show_null_heatmap = st.sidebar.checkbox("Show Null Heatmap", value=True,
                                            help="Heatmap showing missing value patterns")
    show_null_correlation = st.sidebar.checkbox("Show Null Correlation", value=False,
                                                help="Correlation between missing value patterns")

    # Distribution analysis options
    st.sidebar.markdown("**📊 Distribution Analysis**")
    show_distributions = st.sidebar.checkbox("Show Distributions", value=True,
                                             help="Histograms for numeric columns")
    show_box_plots = st.sidebar.checkbox("Show Box Plots", value=True,
                                         help="Box plots showing outliers and quartiles")

    # Correlation analysis options
    st.sidebar.markdown("**🔗 Correlation Analysis**")
    show_correlation = st.sidebar.checkbox("Show Correlation Heatmap", value=True,
                                           help="Correlation matrix for numeric columns")
    correlation_method = st.sidebar.selectbox("Correlation Method",
                                              ["pearson", "spearman", "kendall"],
                                              help="Method for calculating correlations")
    show_correlation_strength = st.sidebar.checkbox("Show Correlation Distribution", value=False,
                                                    help="Distribution of correlation strengths")

    # Categorical analysis options
    st.sidebar.markdown("**📂 Categorical Analysis**")
    show_categorical = st.sidebar.checkbox("Show Categorical Counts", value=True,
                                           help="Value counts for categorical columns")
    categorical_top_k = st.sidebar.slider("Top K Categories", min_value=5, max_value=20,
                                          value=10, help="Number of top categories to show")
    show_categorical_diversity = st.sidebar.checkbox("Show Categorical Diversity", value=False,
                                                     help="Diversity metrics for categorical data")

    st.sidebar.markdown("---")

    # Advanced options
    with st.sidebar.expander("⚙️ Advanced Options", expanded=False):
        # Outlier detection
        enable_outlier_detection = st.checkbox("Enable Outlier Detection", value=False,
                                               help="Detect outliers using IQR or Z-score methods")
        outlier_method = st.selectbox("Outlier Detection Method",
                                      ["IQR", "Z-score"],
                                      help="Method for detecting outliers")
        outlier_threshold = st.slider("Outlier Threshold",
                                      min_value=1.5, max_value=5.0, value=3.0, step=0.1,
                                      help="Threshold for outlier detection")

        # Sampling options
        enable_sampling = st.checkbox("Enable Data Sampling", value=False,
                                      help="Sample large datasets for faster processing")
        sample_size = st.number_input("Sample Size", min_value=1000, max_value=50000,
                                      value=10000, step=1000,
                                      help="Number of rows to sample for visualization")

        # Chart customization
        figure_dpi = st.slider("Figure DPI", min_value=50, max_value=300, value=100,
                               help="Resolution of generated charts")
        color_palette = st.selectbox("Color Palette",
                                     ["husl", "viridis", "plasma", "Set3", "tab10"],
                                     help="Color scheme for charts")

    st.sidebar.markdown("---")

    # Export options
    with st.sidebar.expander("📄 Export Options", expanded=False):
        enable_pdf_export = st.checkbox("Enable PDF Export", value=False,
                                        help="Generate downloadable PDF report")
        include_raw_data = st.checkbox("Include Raw Data in Export", value=False,
                                       help="Include summary tables in PDF")

    # Compile all options into a dictionary
    options = {
        # Data overview
        'show_summary': show_summary,
        'show_memory_usage': show_memory_usage,

        # Null analysis
        'show_null_bar': show_null_bar,
        'show_null_heatmap': show_null_heatmap,
        'show_null_correlation': show_null_correlation,

        # Distribution analysis
        'show_distributions': show_distributions,
        'show_box_plots': show_box_plots,

        # Correlation analysis
        'show_correlation': show_correlation,
        'correlation_method': correlation_method,
        'show_correlation_strength': show_correlation_strength,

        # Categorical analysis
        'show_categorical': show_categorical,
        'categorical_top_k': categorical_top_k,
        'show_categorical_diversity': show_categorical_diversity,

        # Advanced options
        'enable_outlier_detection': enable_outlier_detection,
        'outlier_method': outlier_method,
        'outlier_threshold': outlier_threshold,
        'enable_sampling': enable_sampling,
        'sample_size': sample_size,
        'figure_dpi': figure_dpi,
        'color_palette': color_palette,

        # Export options
        'enable_pdf_export': enable_pdf_export,
        'include_raw_data': include_raw_data
    }

    return uploaded_file, options


def render_sidebar_info(df_info: Dict[str, Any]) -> None:
    """
    Display additional information about the loaded dataset in the sidebar.

    Args:
        df_info (dict): Dictionary containing dataset information
    """
    if df_info:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Dataset Info")

        # Basic metrics
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Rows", f"{df_info.get('rows', 0):,}")
            st.metric(
                "Memory", f"{df_info.get('memory_usage', 0) / 1024**2:.1f} MB")

        with col2:
            st.metric("Columns", df_info.get('columns', 0))
            st.metric("Nulls", f"{df_info.get('null_counts', 0):,}")

        # Data type breakdown
        dtypes_info = df_info.get('dtypes', {})
        if dtypes_info:
            st.sidebar.markdown("**Data Types:**")
            for dtype, count in dtypes_info.items():
                st.sidebar.text(f"• {dtype}: {count}")

        # Quality indicators
        duplicate_rows = df_info.get('duplicate_rows', 0)
        if duplicate_rows > 0:
            st.sidebar.warning(f"⚠️ {duplicate_rows:,} duplicate rows found")


def render_processing_status() -> None:
    """
    Show processing status and tips while visualizations are being generated.
    """
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔄 Processing Status")

    # Tips for users
    with st.sidebar.expander("💡 Tips", expanded=True):
        st.markdown("""
        **Quick Tips:**
        - Start with basic visualizations first
        - Use sampling for datasets > 10K rows
        - Check for missing values patterns
        - Look for correlations > 0.7 or < -0.7
        - Categorical columns with high cardinality may take longer
        """)

    # Performance recommendations
    st.sidebar.info("""
    💡 **Performance Tip:** 
    For large datasets, enable sampling to speed up processing.
    """)
