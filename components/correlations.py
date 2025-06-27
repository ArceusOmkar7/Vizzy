"""
Correlations Tab Component

Displays correlation analysis and relationship insights between numeric variables.
"""

import streamlit as st
import pandas as pd
import numpy as np
from visuals.correlation import plot_correlation_heatmap, find_strong_correlations
from utils.data_checks import get_numeric_columns


def render_correlations_tab(df):
    """
    Render the correlations tab with correlation analysis.

    Args:
        df (pd.DataFrame): Input dataframe
    """
    st.header("🔗 Correlations")

    # Get numeric columns
    numeric_cols = get_numeric_columns(df)

    if len(numeric_cols) < 2:
        st.warning("⚠️ Need at least 2 numeric columns for correlation analysis.")
        st.info("💡 Try uploading a dataset with more numeric variables.")
        return

    # Configuration section
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.subheader("🎯 Correlation Settings")

    with col2:
        method = st.selectbox(
            "Method:",
            ["pearson", "spearman", "kendall"],
            help="Pearson: linear relationships, Spearman: monotonic relationships"
        )

    with col3:
        show_values = st.checkbox("Show values", value=True)

    # Main correlation heatmap
    st.subheader("🌡️ Correlation Heatmap")

    try:
        fig = plot_correlation_heatmap(
            df[numeric_cols],
            method=method,
            annot=show_values,
            figsize=(12, 8)
        )
        st.pyplot(fig)

        # Strong correlations summary
        st.subheader("💪 Strong Correlations")

        # Find correlations above threshold
        threshold = st.slider("Correlation threshold:", 0.1, 1.0, 0.7, 0.1)

        strong_corrs = find_strong_correlations(
            df[numeric_cols], threshold=threshold, method=method)

        if not strong_corrs.empty:
            # Format the correlations table
            strong_corrs_display = strong_corrs.copy()
            strong_corrs_display['Correlation'] = strong_corrs_display['Correlation'].apply(
                lambda x: f"{x:.3f}")
            strong_corrs_display['Strength'] = strong_corrs_display['Correlation'].astype(float).apply(
                lambda x: "🔴 Very Strong" if abs(x) >= 0.9
                else "🟠 Strong" if abs(x) >= 0.7
                else "🟡 Moderate"
            )

            st.dataframe(
                strong_corrs_display[['Variable 1',
                                      'Variable 2', 'Correlation', 'Strength']],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info(
                f"🔍 No correlations found above {threshold:.1f} threshold.")

    except Exception as e:
        st.error(f"❌ Error creating correlation analysis: {str(e)}")

    # Quick insights
    if len(numeric_cols) >= 2:
        st.subheader("💡 Quick Insights")

        # Calculate correlation matrix
        corr_matrix = df[numeric_cols].corr(method=method)

        # Find highest correlation
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        corr_matrix_masked = corr_matrix.mask(mask)

        max_corr = corr_matrix_masked.abs().max().max()
        if not np.isnan(max_corr):
            max_idx = corr_matrix_masked.abs().stack().idxmax()

            col1, col2 = st.columns(2)
            with col1:
                st.metric(
                    "Strongest correlation",
                    f"{corr_matrix.loc[max_idx]:.3f}",
                    f"Between {max_idx[0]} & {max_idx[1]}"
                )

            with col2:
                avg_corr = corr_matrix_masked.abs().mean().mean()
                st.metric(
                    "Average correlation",
                    f"{avg_corr:.3f}",
                    "Across all numeric pairs"
                )
