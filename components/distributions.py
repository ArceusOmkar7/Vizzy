"""
Distributions Tab Component

Analyzes the distribution of numeric variables with histograms and box plots.
"""

import streamlit as st
import pandas as pd
import numpy as np
from visuals.distributions import plot_numeric_distributions, plot_box_plots


def render_distributions_tab(df):
    """
    Render the distributions analysis tab.

    Args:
        df (pd.DataFrame): Input dataframe
    """
    st.header("📊 Distribution Analysis")

    # Get numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if not numeric_cols:
        st.info("📝 No numeric columns found for distribution analysis.")
        st.markdown("""
        **Distribution analysis requires numeric data types such as:**
        - Integers (int64, int32, etc.)
        - Floating point numbers (float64, float32, etc.)
        - Numeric data in general
        
        Your dataset appears to contain only categorical or text data.
        """)
        return

    st.write(f"Found **{len(numeric_cols)}** numeric columns for analysis.")

    # Column selection for focused analysis
    col1, col2 = st.columns([2, 1])

    with col1:
        selected_cols = st.multiselect(
            "Select specific columns (optional - leave empty for all):",
            numeric_cols,
            help="Choose specific columns to analyze, or leave empty to analyze all numeric columns",
            key="dist_column_selector"
        )

    with col2:
        n_bins = st.slider("Number of histogram bins:", 10,
                           50, 30, key="dist_bins_slider")

    # Use selected columns or all numeric columns
    cols_to_analyze = selected_cols if selected_cols else numeric_cols

    # Limit number of columns for performance
    if len(cols_to_analyze) > 8:
        st.warning(
            f"⚠️ Too many columns selected ({len(cols_to_analyze)}). Showing first 8 for performance.")
        cols_to_analyze = cols_to_analyze[:8]

    # Distribution plots
    st.subheader("📈 Histograms")
    st.markdown(
        "Shows the frequency distribution of values in each numeric column.")

    with st.spinner("Generating distribution plots..."):
        fig_dist = plot_numeric_distributions(
            df, columns=cols_to_analyze, bins=n_bins)
        st.pyplot(fig_dist)
        import matplotlib.pyplot as plt
        plt.close(fig_dist)

    # Box plots
    st.subheader("📦 Box Plots")
    st.markdown("Shows quartiles, outliers, and spread of the data.")

    with st.spinner("Generating box plots..."):
        fig_box = plot_box_plots(df, columns=cols_to_analyze)
        st.pyplot(fig_box)
        plt.close(fig_box)

    # Summary statistics
    st.subheader("📊 Summary Statistics")

    # Calculate summary statistics for selected columns
    summary_stats = df[cols_to_analyze].describe()
    st.dataframe(summary_stats, use_container_width=True)

    # Download button for statistics
    csv = summary_stats.to_csv()
    st.download_button(
        label="📥 Download Summary Statistics",
        data=csv,
        file_name="distribution_summary_stats.csv",
        mime="text/csv"
    )

    # Distribution insights
    st.subheader("🔍 Distribution Insights")

    insights = []

    for col in cols_to_analyze:
        data = df[col].dropna()
        if len(data) == 0:
            continue

        # Basic statistics
        skewness = data.skew()
        kurtosis = data.kurtosis()

        # Analyze distribution shape
        if abs(skewness) < 0.5:
            skew_desc = "approximately symmetric"
        elif skewness > 0.5:
            skew_desc = "right-skewed (positive skew)"
        else:
            skew_desc = "left-skewed (negative skew)"

        if abs(kurtosis) < 0.5:
            kurt_desc = "normal tail thickness"
        elif kurtosis > 0.5:
            kurt_desc = "heavy tails"
        else:
            kurt_desc = "light tails"

        insights.append({
            'Column': col,
            'Shape': skew_desc,
            'Tails': kurt_desc,
            'Skewness': f"{skewness:.2f}",
            'Kurtosis': f"{kurtosis:.2f}",
            'Range': f"{data.min():.2f} to {data.max():.2f}",
            'IQR': f"{data.quantile(0.75) - data.quantile(0.25):.2f}"
        })

    if insights:
        insights_df = pd.DataFrame(insights)
        st.dataframe(insights_df, use_container_width=True)

    # Distribution interpretation guide
    with st.expander("📚 How to Interpret Distributions", expanded=False):
        st.markdown("""
        **Histogram Interpretation:**
        - **Bell-shaped**: Normal distribution, most values around the center
        - **Right-skewed**: Long tail on the right, most values on the left
        - **Left-skewed**: Long tail on the left, most values on the right
        - **Bimodal**: Two peaks, might indicate two different groups
        
        **Box Plot Interpretation:**
        - **Box**: Contains 50% of the data (25th to 75th percentile)
        - **Line in box**: Median (50th percentile)
        - **Whiskers**: Extend to 1.5 × IQR from the box
        - **Dots**: Outliers beyond the whiskers
        
        **Skewness Values:**
        - **-0.5 to 0.5**: Approximately symmetric
        - **> 0.5**: Right-skewed (positive skew)
        - **< -0.5**: Left-skewed (negative skew)
        """)

    # Outlier detection summary
    if len(cols_to_analyze) <= 5:  # Only for small number of columns
        st.subheader("🎯 Outlier Detection Summary")

        outlier_summary = []
        for col in cols_to_analyze:
            data = df[col].dropna()
            if len(data) == 0:
                continue

            # IQR method
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = data[(data < lower_bound) | (data > upper_bound)]
            outlier_percentage = (len(outliers) / len(data)) * 100

            outlier_summary.append({
                'Column': col,
                'Outliers Count': len(outliers),
                'Outliers %': f"{outlier_percentage:.1f}%",
                'Lower Bound': f"{lower_bound:.2f}",
                'Upper Bound': f"{upper_bound:.2f}"
            })

        if outlier_summary:
            outlier_df = pd.DataFrame(outlier_summary)
            st.dataframe(outlier_df, use_container_width=True)

            high_outliers = [row['Column'] for _, row in outlier_df.iterrows()
                             if float(row['Outliers %'].rstrip('%')) > 5]

            if high_outliers:
                st.warning(
                    f"⚠️ **High outlier percentage (>5%) in:** {', '.join(high_outliers)}")
                st.info(
                    "💡 Consider investigating these outliers - they might be data entry errors or genuine extreme values.")

    else:
        st.info("💡 Select fewer columns (≤5) to see detailed outlier analysis.")
