"""
Data Overview Tab Component

Displays basic data information, column summary, data types, and data quality scoring.
"""

import streamlit as st
import pandas as pd
from visuals.summary import create_summary_table, plot_data_types_summary
from visuals.quality_score import (
    create_quality_score_gauge, create_dimension_scores_chart,
    create_column_quality_heatmap, create_missing_values_overview,
    create_data_types_distribution, create_quality_recommendations_display,
    create_detailed_issues_table
)
from utils.data_checks import get_column_summary
from utils.quality_engine import DataQualityEngine, get_column_quality_details


def render_data_overview_tab(df):
    """
    Render the data overview tab with essential dataset information and quality scoring.

    Args:
        df (pd.DataFrame): Input dataframe
    """
    st.header("📋 Data Overview")

    # Data Quality Scoring Section
    st.subheader("🎯 Data Quality Assessment")

    with st.spinner("Calculating data quality scores..."):
        quality_engine = DataQualityEngine(df)
        quality_results = quality_engine.calculate_overall_score()

    # Display overall quality score
    col1, col2 = st.columns([1, 2])

    with col1:
        # Quality score gauge
        palette_name = getattr(
            st.session_state, 'color_palette', 'Default (Husl)')
        gauge_fig = create_quality_score_gauge(
            quality_results['overall_score'],
            quality_results['grade'],
            palette_name
        )
        st.plotly_chart(gauge_fig, use_container_width=True)

    with col2:
        # Quality summary and grade
        st.markdown(f"### Quality Grade: **{quality_results['grade']}**")
        st.markdown(f"**Score**: {quality_results['overall_score']}/100")
        st.markdown(quality_results['summary'])

        # Quick stats
        st.markdown("**Quick Stats:**")
        missing_pct = (df.isnull().sum().sum() /
                       (len(df) * len(df.columns))) * 100
        duplicate_pct = (df.duplicated().sum() / len(df)) * 100
        st.markdown(f"• Missing data: {missing_pct:.1f}%")
        st.markdown(f"• Duplicate rows: {duplicate_pct:.1f}%")
        st.markdown(f"• Data types: {df.dtypes.nunique()} different types")

    # Quality dimensions breakdown
    st.subheader("📊 Quality Dimensions Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        dimension_fig = create_dimension_scores_chart(
            quality_results['dimensions'], palette_name)
        st.plotly_chart(dimension_fig, use_container_width=True)

    with col2:
        # Recommendations
        st.markdown("### 💡 Recommendations")
        recommendations_text = create_quality_recommendations_display(
            quality_results['recommendations'])
        st.markdown(recommendations_text)

    # Detailed quality issues
    with st.expander("🔍 Detailed Quality Issues", expanded=False):
        issues_df = create_detailed_issues_table(quality_results['dimensions'])
        st.dataframe(issues_df, use_container_width=True)

        # Download quality report
        quality_csv = issues_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Quality Report",
            data=quality_csv,
            file_name=f"quality_report_{df.shape[0]}x{df.shape[1]}.csv",
            mime="text/csv"
        )

    # Column-level quality analysis
    with st.expander("📋 Column Quality Details", expanded=False):
        col_quality_df = get_column_quality_details(df)
        st.dataframe(col_quality_df, use_container_width=True)

        # Column quality heatmap
        if len(df.columns) <= 20:  # Only show heatmap for reasonable number of columns
            st.markdown("**Column Quality Heatmap**")
            quality_heatmap = create_column_quality_heatmap(df, palette_name)
            st.pyplot(quality_heatmap)
            import matplotlib.pyplot as plt
            plt.close(quality_heatmap)
        else:
            st.info(
                "Too many columns to display heatmap. Use the table above for column quality details.")

    st.markdown("---")  # Separator

    # Show first few rows
    st.subheader("🔍 Data Preview")
    col1, col2 = st.columns([3, 1])

    with col2:
        n_rows = st.selectbox("Rows to display:", [5, 10, 20, 50], index=0)

    with col1:
        st.dataframe(df.head(n_rows), use_container_width=True)

    # Column information
    st.subheader("📊 Column Information")

    col1, col2 = st.columns(2)

    with col1:
        # Data types summary
        st.markdown("**Data Types**")
        dtype_counts = df.dtypes.value_counts()
        for dtype, count in dtype_counts.items():
            st.write(f"• **{dtype}**: {count} columns")

    with col2:
        # Basic statistics
        st.markdown("**Dataset Statistics**")
        stats = {
            "Total cells": len(df) * len(df.columns),
            "Missing cells": df.isnull().sum().sum(),
            "Complete rows": len(df) - df.isnull().any(axis=1).sum(),
            "Duplicate rows": df.duplicated().sum()
        }

        for key, value in stats.items():
            st.write(f"• **{key}**: {value:,}")

    # Detailed column summary table
    st.subheader("📋 Detailed Column Summary")

    with st.expander("View detailed statistics for all columns", expanded=False):
        summary_df = create_summary_table(df)
        st.dataframe(summary_df, use_container_width=True)

        # Download button
        csv = summary_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Column Summary",
            data=csv,
            file_name=f"column_summary_{df.shape[0]}x{df.shape[1]}.csv",
            mime="text/csv"
        )

    # Data types visualization
    st.subheader("🎨 Data Types Visualization")

    col1, col2 = st.columns(2)

    with col1:
        if len(df.columns) > 1:
            with st.spinner("Generating data types chart..."):
                fig = plot_data_types_summary(df)
                st.pyplot(fig)
                import matplotlib.pyplot as plt
                plt.close(fig)
        else:
            st.info("Need multiple columns to create data types visualization.")

    with col2:
        # Data types distribution pie chart
        types_fig = create_data_types_distribution(df, palette_name)
        st.plotly_chart(types_fig, use_container_width=True)

    # Sample of each column type
    st.subheader("🔬 Sample Values by Data Type")

    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(
        include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

    if numeric_cols:
        with st.expander(f"🔢 Numeric Columns ({len(numeric_cols)})", expanded=False):
            for col in numeric_cols[:5]:  # Show first 5
                unique_vals = df[col].dropna().unique()[:10]
                st.write(f"**{col}**: {', '.join(map(str, unique_vals))}...")

    if categorical_cols:
        with st.expander(f"📝 Categorical Columns ({len(categorical_cols)})", expanded=False):
            for col in categorical_cols[:5]:  # Show first 5
                unique_vals = df[col].dropna().unique()[:10]
                st.write(f"**{col}**: {', '.join(map(str, unique_vals))}...")

    if datetime_cols:
        with st.expander(f"📅 DateTime Columns ({len(datetime_cols)})", expanded=False):
            for col in datetime_cols:
                min_date = df[col].min()
                max_date = df[col].max()
                st.write(f"**{col}**: {min_date} to {max_date}")
