"""
Categorical Tab Component

Displays categorical data analysis including value counts and frequency distributions.
"""

import streamlit as st
import pandas as pd
import numpy as np
from visuals.categories import plot_categorical_counts
from utils.data_checks import get_categorical_columns


def render_categorical_tab(df):
    """
    Render the categorical analysis tab.

    Args:
        df (pd.DataFrame): Input dataframe
    """
    st.header("📂 Categories")

    # Get categorical columns
    categorical_cols = get_categorical_columns(df)

    if not categorical_cols:
        st.warning("⚠️ No categorical columns found in the dataset.")
        st.info("💡 Try uploading a dataset with text or categorical variables.")
        return

    # Configuration section
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.subheader("🎯 Analysis Settings")

    with col2:
        top_k = st.selectbox("Top categories:", [5, 10, 15, 20], index=1)

    with col3:
        show_percentages = st.checkbox("Show percentages", value=True)

    # Column selection
    if len(categorical_cols) > 1:
        selected_cols = st.multiselect(
            "Select columns to analyze:",
            categorical_cols,
            default=categorical_cols[:min(4, len(categorical_cols))],
            help="Select up to 4 columns for detailed analysis"
        )
    else:
        selected_cols = categorical_cols

    if not selected_cols:
        st.info("👆 Please select at least one categorical column to analyze.")
        return

    # Limit to maximum 4 columns for performance
    selected_cols = selected_cols[:4]

    # Value counts visualization
    st.subheader("📊 Value Counts")

    try:
        fig = plot_categorical_counts(
            df,
            columns=selected_cols,
            top_k=top_k,
            min_frequency=1
        )
        st.pyplot(fig)

    except Exception as e:
        st.error(f"❌ Error creating categorical plots: {str(e)}")

    # Detailed analysis for each column
    st.subheader("🔍 Detailed Analysis")

    for col in selected_cols:
        with st.expander(f"📋 {col}", expanded=len(selected_cols) == 1):
            col_data = df[col].dropna()

            if col_data.empty:
                st.warning(f"⚠️ Column '{col}' contains only missing values.")
                continue

            # Basic statistics
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Unique Values", col_data.nunique())

            with col2:
                most_common = col_data.mode(
                ).iloc[0] if not col_data.mode().empty else "N/A"
                st.metric("Most Common", str(most_common)[
                          :15] + "..." if len(str(most_common)) > 15 else str(most_common))

            with col3:
                missing_pct = (df[col].isnull().sum() / len(df)) * 100
                st.metric("Missing %", f"{missing_pct:.1f}%")

            with col4:
                if col_data.nunique() > 0:
                    top_freq = col_data.value_counts().iloc[0]
                    top_pct = (top_freq / len(col_data)) * 100
                    st.metric("Top Category %", f"{top_pct:.1f}%")

            # Value counts table
            st.write("**Top Categories:**")
            value_counts = col_data.value_counts().head(top_k)

            if show_percentages:
                percentages = (value_counts / len(col_data) * 100).round(1)
                counts_df = pd.DataFrame({
                    'Category': value_counts.index,
                    'Count': value_counts.values,
                    'Percentage': percentages.values
                })
                counts_df['Percentage'] = counts_df['Percentage'].astype(
                    str) + '%'
            else:
                counts_df = pd.DataFrame({
                    'Category': value_counts.index,
                    'Count': value_counts.values
                })

            st.dataframe(counts_df, use_container_width=True, hide_index=True)

    # Summary insights
    st.subheader("💡 Summary Insights")

    insights = []

    for col in selected_cols:
        col_data = df[col].dropna()
        if col_data.empty:
            continue

        unique_count = col_data.nunique()
        total_count = len(col_data)
        cardinality_ratio = unique_count / total_count

        if cardinality_ratio > 0.8:
            insights.append(
                f"🔍 **{col}** has high cardinality ({unique_count} unique values) - might need grouping")
        elif cardinality_ratio < 0.1:
            insights.append(
                f"📊 **{col}** has low cardinality ({unique_count} unique values) - good for grouping")

        # Check for imbalanced categories
        if unique_count > 1:
            top_category_pct = (
                col_data.value_counts().iloc[0] / len(col_data)) * 100
            if top_category_pct > 80:
                insights.append(
                    f"⚠️ **{col}** is highly imbalanced - top category represents {top_category_pct:.1f}% of data")
            elif top_category_pct < 10:
                insights.append(
                    f"✅ **{col}** is well balanced - most frequent category is only {top_category_pct:.1f}% of data")

    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info("🔄 Select columns to see category insights.")
