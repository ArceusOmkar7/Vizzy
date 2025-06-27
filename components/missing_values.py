"""
Missing Values Tab Component

Focuses on missing value analysis with essential visualizations.
"""

import streamlit as st
import pandas as pd
from visuals.nulls import plot_null_bar_chart, plot_null_heatmap
from utils.data_checks import analyze_null_values


def render_missing_values_tab(df):
    """
    Render the missing values analysis tab.

    Args:
        df (pd.DataFrame): Input dataframe
    """
    st.header("❓ Missing Values Analysis")

    # Analyze null values
    null_analysis = analyze_null_values(df)

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Total Missing",
            f"{null_analysis['total_nulls']:,}",
            delta=f"{(null_analysis['total_nulls'] / (len(df) * len(df.columns)) * 100):.1f}% of all cells"
        )

    with col2:
        st.metric(
            "Columns with Missing",
            len(null_analysis['columns_with_nulls']),
            delta=f"{len(null_analysis['columns_with_nulls']) / len(df.columns) * 100:.1f}% of columns"
        )

    with col3:
        complete_rows = len(df) - df.isnull().any(axis=1).sum()
        st.metric(
            "Complete Rows",
            f"{complete_rows:,}",
            delta=f"{complete_rows / len(df) * 100:.1f}% of rows"
        )

    # Check if there are any missing values
    if null_analysis['total_nulls'] == 0:
        st.success("🎉 No missing values found in this dataset!")
        st.balloons()
        return

    # Warning for problematic columns
    if null_analysis['completely_null_columns']:
        st.error(
            f"⚠️ **Completely empty columns found:** {', '.join(null_analysis['completely_null_columns'])}")

    if null_analysis['mostly_null_columns']:
        st.warning(
            f"⚠️ **Mostly empty columns (>50% missing):** {', '.join(null_analysis['mostly_null_columns'])}")

    # Missing values visualizations
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Missing Values by Column")
        with st.spinner("Generating bar chart..."):
            fig_bar = plot_null_bar_chart(df)
            st.pyplot(fig_bar)
            import matplotlib.pyplot as plt
            plt.close(fig_bar)

    with col2:
        st.subheader("🔥 Missing Values Pattern")
        if len(df) > 1000:
            st.info("📝 Showing pattern for a sample of 1000 rows for performance.")

        with st.spinner("Generating heatmap..."):
            fig_heatmap = plot_null_heatmap(df)
            st.pyplot(fig_heatmap)
            plt.close(fig_heatmap)

    # Detailed missing values table
    st.subheader("📋 Missing Values Summary")

    missing_summary = []
    for col in df.columns:
        missing_count = df[col].isnull().sum()
        if missing_count > 0:
            missing_summary.append({
                'Column': col,
                'Missing Count': missing_count,
                'Missing %': f"{(missing_count / len(df)) * 100:.1f}%",
                'Data Type': str(df[col].dtype),
                'Non-null Count': df[col].count()
            })

    if missing_summary:
        missing_df = pd.DataFrame(missing_summary)
        missing_df = missing_df.sort_values('Missing Count', ascending=False)
        st.dataframe(missing_df, use_container_width=True)

        # Download button
        csv = missing_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Missing Values Report",
            data=csv,
            file_name="missing_values_report.csv",
            mime="text/csv"
        )

    # Recommendations
    st.subheader("💡 Recommendations")

    recommendations = []

    if null_analysis['completely_null_columns']:
        recommendations.append("🗑️ Consider removing completely empty columns")

    if null_analysis['mostly_null_columns']:
        recommendations.append("⚠️ Review columns with >50% missing values")

    missing_percentage = (
        null_analysis['total_nulls'] / (len(df) * len(df.columns))) * 100
    if missing_percentage > 20:
        recommendations.append(
            "📊 High missing data percentage - consider data quality review")
    elif missing_percentage > 10:
        recommendations.append(
            "📝 Moderate missing data - consider imputation strategies")
    else:
        recommendations.append(
            "✅ Low missing data percentage - dataset is relatively complete")

    for rec in recommendations:
        st.write(f"• {rec}")

    # Missing patterns insights
    if len(null_analysis['columns_with_nulls']) > 1:
        with st.expander("🔍 Advanced: Missing Value Patterns", expanded=False):
            st.markdown("""
            **Common missing value patterns:**
            - **Random missing**: Values missing at random across the dataset
            - **Systematic missing**: Missing values follow a pattern (e.g., related to other variables)
            - **Structural missing**: Missing by design (e.g., optional fields)
            
            Use the heatmap above to identify if missing values cluster together.
            """)
