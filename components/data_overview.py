"""
Data Overview Tab Component

Displays basic data information, column summary, and data types.
"""

import streamlit as st
import pandas as pd
from visuals.summary import create_summary_table, plot_data_types_summary
from utils.data_checks import get_column_summary


def render_data_overview_tab(df):
    """
    Render the data overview tab with essential dataset information.

    Args:
        df (pd.DataFrame): Input dataframe
    """
    st.header("📋 Data Overview")

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

    if len(df.columns) > 1:
        with st.spinner("Generating data types chart..."):
            fig = plot_data_types_summary(df)
            st.pyplot(fig)
            import matplotlib.pyplot as plt
            plt.close(fig)
    else:
        st.info("Need multiple columns to create data types visualization.")

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
