"""
Time Series Analysis Tab Component

Displays time series analysis including trend analysis, seasonality, and pattern detection.
"""

import streamlit as st
import pandas as pd
import numpy as np
from visuals.time_series import (
    plot_time_series_overview,
    plot_seasonal_decomposition,
    plot_time_series_patterns,
    plot_rolling_statistics,
    analyze_time_series_stats
)
from utils.data_checks import detect_datetime_columns, prepare_time_series_data


def render_time_series_tab(df):
    """
    Render the time series analysis tab.

    Args:
        df (pd.DataFrame): Input dataframe
    """
    st.header("📈 Time Series Analysis")

    # Detect datetime columns
    datetime_info = detect_datetime_columns(df)

    if not datetime_info['has_time_series'] and not datetime_info['potential_datetime_columns']:
        st.warning("⚠️ No datetime columns detected in the dataset.")

        # Show potential datetime columns if any
        if datetime_info['potential_datetime_columns']:
            st.info("💡 Found potential datetime columns that could be converted:")
            for pot_col in datetime_info['potential_datetime_columns']:
                st.write(
                    f"- **{pot_col['column']}** (confidence: {pot_col['score']:.1%})")
                st.write(
                    f"  Sample values: {', '.join(map(str, pot_col['sample_values']))}")
        else:
            st.info(
                "💡 Try uploading a dataset with date/time columns for time series analysis.")

        return

    # Configuration section
    st.subheader("🎯 Time Series Configuration")

    # DateTime column selection
    datetime_columns = list(datetime_info['datetime_columns'].keys())
    potential_columns = [col['column']
                         for col in datetime_info['potential_datetime_columns']]
    all_datetime_options = datetime_columns + potential_columns

    if not all_datetime_options:
        st.error("No valid datetime columns found.")
        return

    col1, col2 = st.columns(2)

    with col1:
        selected_datetime_col = st.selectbox(
            "Select DateTime Column:",
            all_datetime_options,
            help="Choose the column containing date/time information",
            key="ts_datetime_col_selector"
        )

    # Prepare data for the selected datetime column
    try:
        if selected_datetime_col in datetime_columns:
            # Already a datetime column
            prepared_df = df.copy()
        else:
            # Convert potential datetime column
            prepared_df = df.copy()
            prepared_df[selected_datetime_col] = pd.to_datetime(
                prepared_df[selected_datetime_col], errors='coerce'
            )

        # Get numeric columns for value selection
        numeric_cols = prepared_df.select_dtypes(
            include=[np.number]).columns.tolist()

        if not numeric_cols:
            st.error("No numeric columns found for time series analysis.")
            return

        with col2:
            selected_value_col = st.selectbox(
                "Select Value Column:",
                numeric_cols,
                help="Choose the numeric column to analyze over time",
                key="ts_value_col_selector"
            )

        # Additional options
        col3, col4 = st.columns(2)

        with col3:
            show_patterns = st.checkbox(
                "Show Pattern Analysis", value=True, key="ts_show_patterns")

        with col4:
            show_rolling = st.checkbox(
                "Show Rolling Statistics", value=True, key="ts_show_rolling")

    except Exception as e:
        st.error(f"Error preparing time series data: {str(e)}")
        return

    # Filter out invalid dates and prepare final dataset
    ts_data = prepared_df.copy()
    ts_data = ts_data.dropna(
        subset=[selected_datetime_col, selected_value_col])

    if len(ts_data) < 5:
        st.error(
            "Insufficient data points for time series analysis (need at least 5).")
        return

    # Display time series info
    st.subheader("📊 Time Series Information")

    # Calculate and display basic statistics
    ts_stats = analyze_time_series_stats(
        ts_data, selected_datetime_col, selected_value_col)

    if 'error' in ts_stats:
        st.error(f"Error analyzing time series: {ts_stats['error']}")
        return

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Data Points", f"{ts_stats['data_points']:,}")

    with col2:
        st.metric("Date Range", f"{ts_stats['date_range']['days']} days")

    with col3:
        if 'trend' in ts_stats:
            trend_direction = ts_stats['trend']['direction'].title()
            st.metric("Trend", trend_direction)

    with col4:
        missing_pct = (ts_stats['value_stats']
                       ['missing_count'] / ts_stats['data_points']) * 100
        st.metric("Missing Data", f"{missing_pct:.1f}%")

    # Date range information
    with st.expander("📅 Date Range Details", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.write(
                f"**Start Date:** {ts_stats['date_range']['start'].strftime('%Y-%m-%d')}")
            st.write(
                f"**End Date:** {ts_stats['date_range']['end'].strftime('%Y-%m-%d')}")
        with col2:
            st.write(f"**Duration:** {ts_stats['date_range']['days']} days")
            if 'trend' in ts_stats and ts_stats['date_range']['days'] > 0:
                change_per_day = ts_stats['trend']['change_per_day']
                st.write(f"**Daily Change:** {change_per_day:.4f}")

    # Main time series plot
    st.subheader("📈 Time Series Overview")

    try:
        fig_overview = plot_time_series_overview(
            ts_data,
            selected_datetime_col,
            [selected_value_col]
        )
        st.pyplot(fig_overview)

    except Exception as e:
        st.error(f"Error creating time series overview: {str(e)}")

    # Pattern analysis
    if show_patterns:
        st.subheader("🔍 Temporal Patterns")

        try:
            fig_patterns = plot_time_series_patterns(
                ts_data,
                selected_datetime_col,
                selected_value_col
            )
            st.pyplot(fig_patterns)

        except Exception as e:
            st.error(f"Error creating pattern analysis: {str(e)}")

    # Rolling statistics
    if show_rolling:
        st.subheader("📊 Rolling Statistics")

        # Rolling window configuration
        col1, col2 = st.columns(2)

        with col1:
            # Auto-suggest window sizes based on data length
            data_length = len(ts_data)
            if data_length > 365:
                default_windows = [7, 30, 90]
            elif data_length > 30:
                default_windows = [3, 7, 14]
            else:
                default_windows = [3, 5]

            window_input = st.text_input(
                "Rolling Windows (comma-separated):",
                value=",".join(map(str, default_windows)),
                help="Enter window sizes separated by commas (e.g., 7,30,90)",
                key="ts_rolling_windows_input"
            )

        try:
            window_sizes = [int(w.strip()) for w in window_input.split(
                ",") if w.strip().isdigit()]

            if window_sizes:
                fig_rolling = plot_rolling_statistics(
                    ts_data,
                    selected_datetime_col,
                    selected_value_col,
                    window_sizes
                )
                st.pyplot(fig_rolling)
            else:
                st.warning("Please enter valid window sizes.")

        except Exception as e:
            st.error(f"Error creating rolling statistics: {str(e)}")

    # Seasonal decomposition (if statsmodels is available)
    with st.expander("📊 Advanced: Seasonal Decomposition", expanded=False):
        st.markdown("""
        **Seasonal decomposition** breaks down a time series into trend, seasonal, and residual components.
        This analysis requires the `statsmodels` library.
        """)

        if st.button("Run Seasonal Decomposition", key="seasonal_decomp_btn"):
            try:
                # Determine seasonal period
                data_length = len(ts_data)
                if data_length > 365:
                    period = 365  # Yearly seasonality
                elif data_length > 52:
                    period = 52   # Weekly seasonality
                elif data_length > 12:
                    period = 12   # Monthly seasonality
                else:
                    # Quarterly or data-dependent
                    period = max(4, data_length // 4)

                fig_decomp = plot_seasonal_decomposition(
                    ts_data,
                    selected_datetime_col,
                    selected_value_col,
                    period=period
                )
                st.pyplot(fig_decomp)

                st.info(
                    f"💡 Using seasonal period of {period} based on data length.")

            except Exception as e:
                st.error(f"Seasonal decomposition failed: {str(e)}")
                st.info(
                    "💡 Install statsmodels for advanced time series decomposition: `pip install statsmodels`")

    # Time series insights
    st.subheader("💡 Time Series Insights")

    insights = []

    # Trend insights
    if 'trend' in ts_stats:
        trend = ts_stats['trend']
        if abs(trend['slope']) > 0.01:  # Meaningful trend
            direction = trend['direction']
            insights.append(
                f"📈 **Trend Direction**: The data shows a {direction} trend over time.")

            if trend['change_per_day'] != 0:
                abs_change = abs(trend['change_per_day'])
                time_unit = "day" if abs_change >= 0.01 else "month" if abs_change * \
                    30 >= 0.01 else "year"
                change_val = abs_change if time_unit == "day" else abs_change * \
                    30 if time_unit == "month" else abs_change * 365
                insights.append(
                    f"📊 **Rate of Change**: Approximately {change_val:.3f} units per {time_unit}.")

    # Data quality insights
    missing_pct = (ts_stats['value_stats']
                   ['missing_count'] / ts_stats['data_points']) * 100
    if missing_pct > 10:
        insights.append(
            f"⚠️ **Data Quality**: {missing_pct:.1f}% of data points are missing - consider data cleaning.")
    elif missing_pct == 0:
        insights.append(
            "✅ **Data Quality**: No missing values detected in the time series.")

    # Variability insights
    cv = ts_stats['value_stats']['std'] / \
        abs(ts_stats['value_stats']['mean']
            ) if ts_stats['value_stats']['mean'] != 0 else 0
    if cv > 1:
        insights.append(
            "📊 **Variability**: High variability detected - the data has significant fluctuations.")
    elif cv < 0.1:
        insights.append(
            "📊 **Variability**: Low variability - the data is relatively stable over time.")

    # Duration insights
    duration_days = ts_stats['date_range']['days']
    if duration_days > 365:
        insights.append(
            f"⏱️ **Duration**: Long-term data spanning {duration_days // 365} years - good for trend analysis.")
    elif duration_days < 30:
        insights.append(
            "⏱️ **Duration**: Short-term data - consider collecting more data for robust analysis.")

    if insights:
        for insight in insights:
            st.markdown(insight)
    else:
        st.info("🔄 Analyzing time series patterns...")
