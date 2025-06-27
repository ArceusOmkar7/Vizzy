"""
Chart rendering components for Streamlit integration.

Wraps matplotlib figures and handles their display within Streamlit containers.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, Optional
import time

# Import visualization functions
from visuals.nulls import plot_null_bar_chart, plot_null_heatmap, plot_null_correlation
from visuals.summary import (plot_data_types_summary, plot_uniqueness_analysis,
                             create_summary_table, plot_memory_usage)
from visuals.distributions import plot_numeric_distributions, plot_box_plots, plot_distribution_comparison
from visuals.correlation import (plot_correlation_heatmap, plot_correlation_strength_distribution,
                                 plot_top_correlations, plot_correlation_network)
from visuals.categories import (plot_categorical_counts, plot_category_distribution_pie,
                                plot_categorical_relationship, plot_categorical_summary_table,
                                plot_categorical_diversity)
from utils.data_checks import analyze_null_values, analyze_data_types, get_column_summary
from utils.file_loader import sample_dataframe


def render_charts(df: pd.DataFrame, options: Dict[str, Any]) -> None:
    """
    Render all selected charts based on user options.

    Args:
        df (pd.DataFrame): Input dataframe
        options (dict): Dictionary of user-selected options
    """
    # Apply sampling if enabled
    if options.get('enable_sampling', False) and len(df) > options.get('sample_size', 10000):
        original_length = len(df)
        df = sample_dataframe(df, options.get('sample_size', 10000))
        st.info(
            f"📊 Using a sample of {len(df):,} rows from {original_length:,} total rows for faster processing.")

    # Data Summary Section
    if options.get('show_summary', True):
        render_data_summary(df, options)

    # Missing Values Analysis
    if any([options.get('show_null_bar'), options.get('show_null_heatmap'), options.get('show_null_correlation')]):
        render_null_analysis(df, options)

    # Distribution Analysis
    if options.get('show_distributions') or options.get('show_box_plots'):
        render_distribution_analysis(df, options)

    # Correlation Analysis
    if options.get('show_correlation') or options.get('show_correlation_strength'):
        render_correlation_analysis(df, options)

    # Categorical Analysis
    if options.get('show_categorical') or options.get('show_categorical_diversity'):
        render_categorical_analysis(df, options)

    # PDF Export
    if options.get('enable_pdf_export'):
        render_export_section(df, options)


def render_data_summary(df: pd.DataFrame, options: Dict[str, Any]) -> None:
    """
    Render data summary and overview charts.

    Args:
        df (pd.DataFrame): Input dataframe
        options (dict): User options
    """
    st.header("📋 Data Summary & Overview")

    # Summary table
    with st.expander("📊 Detailed Column Summary", expanded=False):
        summary_df = create_summary_table(df)
        st.dataframe(summary_df, use_container_width=True)

        # Download button for summary
        csv = summary_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Summary as CSV",
            data=csv,
            file_name="data_summary.csv",
            mime="text/csv"
        )

    # Data types visualization
    with st.spinner("Generating data type analysis..."):
        fig_types = plot_data_types_summary(df)
        st.pyplot(fig_types)
        plt.close(fig_types)

    # Uniqueness analysis
    with st.spinner("Analyzing column uniqueness..."):
        fig_unique = plot_uniqueness_analysis(df)
        st.pyplot(fig_unique)
        plt.close(fig_unique)

    # Memory usage if requested
    if options.get('show_memory_usage'):
        with st.spinner("Calculating memory usage..."):
            fig_memory = plot_memory_usage(df)
            st.pyplot(fig_memory)
            plt.close(fig_memory)


def render_null_analysis(df: pd.DataFrame, options: Dict[str, Any]) -> None:
    """
    Render missing values analysis charts.

    Args:
        df (pd.DataFrame): Input dataframe
        options (dict): User options
    """
    st.header("🔍 Missing Values Analysis")

    # Analyze null values
    null_analysis = analyze_null_values(df)

    # Show summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Missing Values", f"{null_analysis['total_nulls']:,}")
    with col2:
        st.metric("Columns with Nulls", len(
            null_analysis['columns_with_nulls']))
    with col3:
        st.metric("Completely Null Columns", len(
            null_analysis['completely_null_columns']))
    with col4:
        st.metric("Mostly Null Columns (>50%)", len(
            null_analysis['mostly_null_columns']))

    # Warning for completely null columns
    if null_analysis['completely_null_columns']:
        st.warning(
            f"⚠️ Found completely null columns: {', '.join(null_analysis['completely_null_columns'])}")

    # Bar chart
    if options.get('show_null_bar'):
        with st.spinner("Generating null values bar chart..."):
            fig_bar = plot_null_bar_chart(df)
            st.pyplot(fig_bar)
            plt.close(fig_bar)

    # Heatmap
    if options.get('show_null_heatmap'):
        with st.spinner("Generating null values heatmap..."):
            fig_heatmap = plot_null_heatmap(df)
            st.pyplot(fig_heatmap)
            plt.close(fig_heatmap)

    # Correlation of null patterns
    if options.get('show_null_correlation'):
        with st.spinner("Analyzing null value correlations..."):
            fig_corr = plot_null_correlation(df)
            st.pyplot(fig_corr)
            plt.close(fig_corr)


def render_distribution_analysis(df: pd.DataFrame, options: Dict[str, Any]) -> None:
    """
    Render distribution analysis charts.

    Args:
        df (pd.DataFrame): Input dataframe
        options (dict): User options
    """
    st.header("📊 Distribution Analysis")

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    if not numeric_cols:
        st.info("No numeric columns found for distribution analysis.")
        return

    # Histograms
    if options.get('show_distributions'):
        with st.spinner("Generating distribution plots..."):
            fig_dist = plot_numeric_distributions(df)
            st.pyplot(fig_dist)
            plt.close(fig_dist)

    # Box plots
    if options.get('show_box_plots'):
        with st.spinner("Generating box plots..."):
            fig_box = plot_box_plots(df)
            st.pyplot(fig_box)
            plt.close(fig_box)

    # Interactive column selection for detailed analysis
    if len(numeric_cols) > 0:
        with st.expander("🔍 Detailed Distribution Analysis", expanded=False):
            selected_column = st.selectbox("Select a column for detailed analysis:",
                                           numeric_cols)

            # Optional grouping
            categorical_cols = df.select_dtypes(
                include=['object', 'category']).columns.tolist()
            group_by = None
            if categorical_cols:
                group_by = st.selectbox("Group by (optional):",
                                        ['None'] + categorical_cols)
                if group_by == 'None':
                    group_by = None

            if st.button("Generate Detailed Analysis"):
                with st.spinner("Generating detailed distribution analysis..."):
                    fig_detailed = plot_distribution_comparison(
                        df, selected_column, group_by)
                    st.pyplot(fig_detailed)
                    plt.close(fig_detailed)


def render_correlation_analysis(df: pd.DataFrame, options: Dict[str, Any]) -> None:
    """
    Render correlation analysis charts.

    Args:
        df (pd.DataFrame): Input dataframe
        options (dict): User options
    """
    st.header("🔗 Correlation Analysis")

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

    if len(numeric_cols) < 2:
        st.info("Need at least 2 numeric columns for correlation analysis.")
        return

    method = options.get('correlation_method', 'pearson')

    # Main correlation heatmap
    if options.get('show_correlation'):
        with st.spinner(f"Generating {method} correlation heatmap..."):
            fig_corr = plot_correlation_heatmap(df, method=method)
            st.pyplot(fig_corr)
            plt.close(fig_corr)

    # Correlation strength distribution
    if options.get('show_correlation_strength'):
        with st.spinner("Analyzing correlation strength distribution..."):
            fig_strength = plot_correlation_strength_distribution(
                df, method=method)
            st.pyplot(fig_strength)
            plt.close(fig_strength)

    # Additional correlation insights
    with st.expander("🎯 Top Correlations & Insights", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            min_correlation = st.slider("Minimum correlation threshold:",
                                        min_value=0.1, max_value=0.9, value=0.3, step=0.1)
            top_n = st.slider("Number of top correlations:",
                              min_value=5, max_value=20, value=10)

        with col2:
            show_network = st.checkbox("Show correlation network", value=False)
            network_threshold = st.slider("Network threshold:",
                                          min_value=0.3, max_value=0.9, value=0.5, step=0.1)

        if st.button("Generate Correlation Insights"):
            with st.spinner("Generating correlation insights..."):
                # Top correlations
                fig_top = plot_top_correlations(df, method=method, top_n=top_n,
                                                min_correlation=min_correlation)
                st.pyplot(fig_top)
                plt.close(fig_top)

                # Network plot if requested
                if show_network:
                    fig_network = plot_correlation_network(df, method=method,
                                                           threshold=network_threshold)
                    st.pyplot(fig_network)
                    plt.close(fig_network)


def render_categorical_analysis(df: pd.DataFrame, options: Dict[str, Any]) -> None:
    """
    Render categorical data analysis charts.

    Args:
        df (pd.DataFrame): Input dataframe
        options (dict): User options
    """
    st.header("📂 Categorical Data Analysis")

    categorical_cols = df.select_dtypes(
        include=['object', 'category']).columns.tolist()

    if not categorical_cols:
        st.info("No categorical columns found for analysis.")
        return

    # Value counts for all categorical columns
    if options.get('show_categorical'):
        top_k = options.get('categorical_top_k', 10)
        with st.spinner("Generating categorical value counts..."):
            fig_cat = plot_categorical_counts(df, top_k=top_k)
            st.pyplot(fig_cat)
            plt.close(fig_cat)

    # Categorical diversity analysis
    if options.get('show_categorical_diversity'):
        with st.spinner("Analyzing categorical diversity..."):
            fig_diversity = plot_categorical_diversity(df)
            st.pyplot(fig_diversity)
            plt.close(fig_diversity)

    # Interactive categorical analysis
    with st.expander("🔍 Detailed Categorical Analysis", expanded=False):
        selected_cat_col = st.selectbox(
            "Select a categorical column:", categorical_cols)

        analysis_type = st.radio("Analysis type:",
                                 ["Pie Chart", "Relationship Analysis", "Summary Table"])

        if analysis_type == "Pie Chart":
            if st.button("Generate Pie Chart"):
                with st.spinner("Generating pie chart..."):
                    fig_pie = plot_category_distribution_pie(
                        df, selected_cat_col)
                    st.pyplot(fig_pie)
                    plt.close(fig_pie)

        elif analysis_type == "Relationship Analysis":
            if len(categorical_cols) > 1:
                other_cat_cols = [
                    col for col in categorical_cols if col != selected_cat_col]
                selected_cat_col2 = st.selectbox("Select second categorical column:",
                                                 other_cat_cols)
                normalize = st.checkbox("Show percentages", value=True)

                if st.button("Generate Relationship Analysis"):
                    with st.spinner("Generating relationship analysis..."):
                        fig_rel = plot_categorical_relationship(df, selected_cat_col,
                                                                selected_cat_col2, normalize)
                        st.pyplot(fig_rel)
                        plt.close(fig_rel)
            else:
                st.info(
                    "Need at least 2 categorical columns for relationship analysis.")

        elif analysis_type == "Summary Table":
            if st.button("Generate Summary Table"):
                summary_table = plot_categorical_summary_table(
                    df, [selected_cat_col])
                st.dataframe(summary_table, use_container_width=True)


def render_export_section(df: pd.DataFrame, options: Dict[str, Any]) -> None:
    """
    Render export options and PDF generation.

    Args:
        df (pd.DataFrame): Input dataframe
        options (dict): User options
    """
    st.header("📄 Export Options")

    st.info("🚧 PDF export functionality coming soon! For now, you can:")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Download Summary CSV"):
            summary_df = create_summary_table(df)
            csv = summary_df.to_csv(index=False)
            st.download_button(
                label="📥 Download Summary",
                data=csv,
                file_name="data_summary.csv",
                mime="text/csv"
            )

    with col2:
        if st.button("📈 Screenshot Charts"):
            st.info(
                "Use your browser's print function or screenshot tool to save charts.")

    with col3:
        if st.button("💾 Save Analysis"):
            st.info("Bookmark this page or save the generated insights manually.")


def display_chart_with_error_handling(chart_function, *args, **kwargs):
    """
    Display a chart with proper error handling and user feedback.

    Args:
        chart_function: Function that generates the chart
        *args: Arguments for the chart function
        **kwargs: Keyword arguments for the chart function
    """
    try:
        with st.spinner("Generating chart..."):
            start_time = time.time()
            fig = chart_function(*args, **kwargs)
            end_time = time.time()

            st.pyplot(fig)
            plt.close(fig)

            # Show generation time for performance feedback
            if end_time - start_time > 2:
                st.caption(
                    f"⏱️ Chart generated in {end_time - start_time:.1f} seconds")

    except Exception as e:
        st.error(f"Error generating chart: {str(e)}")
        st.info("Try adjusting your settings or contact support if the issue persists.")


def show_chart_info(chart_type: str, description: str) -> None:
    """
    Display information about a chart type.

    Args:
        chart_type (str): Name of the chart type
        description (str): Description of what the chart shows
    """
    with st.expander(f"ℹ️ About {chart_type}", expanded=False):
        st.markdown(description)
