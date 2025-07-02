"""
Time Series Analysis and Visualization Functions

Creates time series plots, trend analysis, seasonality detection, and forecasting visualizations.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import streamlit as st
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime, timedelta
from style import apply_chart_theme, get_color_palette


def plot_time_series_overview(df: pd.DataFrame, datetime_col: str, value_cols: List[str] = None) -> plt.Figure:
    """
    Create an overview plot of time series data.

    Args:
        df (pd.DataFrame): Input dataframe with datetime index or column
        datetime_col (str): Name of datetime column
        value_cols (List[str], optional): List of value columns to plot

    Returns:
        plt.Figure: Matplotlib figure object
    """
    # Prepare the data
    ts_df = df.copy()

    if datetime_col not in ts_df.columns:
        return _create_error_figure("Datetime column not found")

    # Convert datetime column
    ts_df[datetime_col] = pd.to_datetime(ts_df[datetime_col], errors='coerce')
    ts_df = ts_df.dropna(subset=[datetime_col])

    if len(ts_df) == 0:
        return _create_error_figure("No valid datetime data found")

    # Sort by datetime
    ts_df = ts_df.sort_values(datetime_col)

    # Select numeric columns if not specified
    if value_cols is None:
        numeric_cols = ts_df.select_dtypes(
            include=[np.number]).columns.tolist()
        value_cols = numeric_cols[:5]  # Limit to 5 for readability
    else:
        value_cols = [col for col in value_cols if col in ts_df.columns
                      and pd.api.types.is_numeric_dtype(ts_df[col])]

    if not value_cols:
        return _create_error_figure("No numeric columns found for time series")

    # Create subplots
    n_cols = len(value_cols)
    fig, axes = plt.subplots(
        min(n_cols, 3), 1, figsize=(14, min(n_cols, 3) * 4))

    if n_cols == 1:
        axes = [axes]
    elif n_cols > 3:
        # If more than 3 columns, show first 3 and note about others
        value_cols = value_cols[:3]
        axes = axes if isinstance(axes, list) or hasattr(
            axes, '__len__') else [axes]

    colors = get_color_palette(len(value_cols),
                               palette_name=getattr(st.session_state, 'color_palette', 'Default (Husl)'))

    for i, col in enumerate(value_cols):
        ax = axes[i] if len(value_cols) > 1 else axes[0]

        # Plot time series
        ax.plot(ts_df[datetime_col], ts_df[col],
                color=colors[i], linewidth=2, alpha=0.8)

        # Customize subplot
        ax.set_title(f'Time Series: {col}', fontweight='bold', fontsize=12)
        ax.set_xlabel('Date')
        ax.set_ylabel(col)
        ax.grid(True, alpha=0.3)

        # Rotate x-axis labels for better readability
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Add trend line if enough data points
        if len(ts_df) > 10:
            z = np.polyfit(range(len(ts_df)),
                           ts_df[col].fillna(ts_df[col].mean()), 1)
            p = np.poly1d(z)
            ax.plot(ts_df[datetime_col], p(range(len(ts_df))),
                    "--", alpha=0.6, color='red', linewidth=1.5, label='Trend')
            ax.legend()

    plt.tight_layout()
    return apply_chart_theme(fig, "Time Series Overview")


def plot_seasonal_decomposition(df: pd.DataFrame, datetime_col: str, value_col: str,
                                period: int = None) -> plt.Figure:
    """
    Create a seasonal decomposition plot.

    Args:
        df (pd.DataFrame): Input dataframe
        datetime_col (str): Name of datetime column
        value_col (str): Name of value column to decompose
        period (int, optional): Seasonal period for decomposition

    Returns:
        plt.Figure: Matplotlib figure object
    """
    try:
        from statsmodels.tsa.seasonal import seasonal_decompose
    except ImportError:
        return _create_error_figure("Statsmodels not available for seasonal decomposition")

    # Prepare data
    ts_df = df.copy()
    ts_df[datetime_col] = pd.to_datetime(ts_df[datetime_col], errors='coerce')
    ts_df = ts_df.dropna(subset=[datetime_col, value_col])
    ts_df = ts_df.sort_values(datetime_col).set_index(datetime_col)

    if len(ts_df) < 20:
        return _create_error_figure("Insufficient data for seasonal decomposition (need at least 20 points)")

    # Determine period if not provided
    if period is None:
        period = min(len(ts_df) // 4, 365)  # Default to quarterly or yearly

    try:
        # Perform decomposition
        decomposition = seasonal_decompose(ts_df[value_col].ffill(),
                                           model='additive', period=period)

        # Create subplots
        fig, axes = plt.subplots(4, 1, figsize=(14, 12))

        colors = get_color_palette(4,
                                   palette_name=getattr(st.session_state, 'color_palette', 'Default (Husl)'))

        # Original data
        axes[0].plot(decomposition.observed.index, decomposition.observed.values,
                     color=colors[0], linewidth=2)
        axes[0].set_title('Original Time Series', fontweight='bold')
        axes[0].grid(True, alpha=0.3)

        # Trend
        axes[1].plot(decomposition.trend.index, decomposition.trend.values,
                     color=colors[1], linewidth=2)
        axes[1].set_title('Trend Component', fontweight='bold')
        axes[1].grid(True, alpha=0.3)

        # Seasonal
        axes[2].plot(decomposition.seasonal.index, decomposition.seasonal.values,
                     color=colors[2], linewidth=2)
        axes[2].set_title('Seasonal Component', fontweight='bold')
        axes[2].grid(True, alpha=0.3)

        # Residual
        axes[3].plot(decomposition.resid.index, decomposition.resid.values,
                     color=colors[3], linewidth=2)
        axes[3].set_title('Residual Component', fontweight='bold')
        axes[3].grid(True, alpha=0.3)

        # Format x-axis
        for ax in axes:
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

        plt.tight_layout()
        return apply_chart_theme(fig, f"Seasonal Decomposition: {value_col}")

    except Exception as e:
        return _create_error_figure(f"Error in seasonal decomposition: {str(e)}")


def plot_time_series_patterns(df: pd.DataFrame, datetime_col: str, value_col: str) -> plt.Figure:
    """
    Create various time series pattern analysis plots.

    Args:
        df (pd.DataFrame): Input dataframe
        datetime_col (str): Name of datetime column
        value_col (str): Name of value column

    Returns:
        plt.Figure: Matplotlib figure object
    """
    # Prepare data
    ts_df = df.copy()
    ts_df[datetime_col] = pd.to_datetime(ts_df[datetime_col], errors='coerce')
    ts_df = ts_df.dropna(subset=[datetime_col, value_col])
    ts_df = ts_df.sort_values(datetime_col)

    if len(ts_df) < 10:
        return _create_error_figure("Insufficient data for pattern analysis")

    # Extract time components
    ts_df['year'] = ts_df[datetime_col].dt.year
    ts_df['month'] = ts_df[datetime_col].dt.month
    ts_df['day_of_week'] = ts_df[datetime_col].dt.day_name()
    ts_df['hour'] = ts_df[datetime_col].dt.hour

    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    colors = get_color_palette(12,
                               palette_name=getattr(st.session_state, 'color_palette', 'Default (Husl)'))

    # Monthly pattern
    if ts_df['month'].nunique() > 1:
        monthly_avg = ts_df.groupby('month')[value_col].mean()
        axes[0, 0].bar(monthly_avg.index, monthly_avg.values,
                       color=colors[:len(monthly_avg)])
        axes[0, 0].set_title('Average by Month', fontweight='bold')
        axes[0, 0].set_xlabel('Month')
        axes[0, 0].set_ylabel(f'Average {value_col}')
        axes[0, 0].grid(True, alpha=0.3)
    else:
        axes[0, 0].text(0.5, 0.5, 'Insufficient monthly data',
                        ha='center', va='center', transform=axes[0, 0].transAxes)
        axes[0, 0].set_title('Monthly Pattern', fontweight='bold')

    # Day of week pattern
    if ts_df['day_of_week'].nunique() > 1:
        dow_order = ['Monday', 'Tuesday', 'Wednesday',
                     'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_avg = ts_df.groupby('day_of_week')[
            value_col].mean().reindex(dow_order)
        axes[0, 1].bar(range(len(dow_avg.dropna())), dow_avg.dropna().values,
                       color=colors[:len(dow_avg.dropna())])
        axes[0, 1].set_title('Average by Day of Week', fontweight='bold')
        axes[0, 1].set_xlabel('Day of Week')
        axes[0, 1].set_ylabel(f'Average {value_col}')
        axes[0, 1].set_xticks(range(len(dow_avg.dropna())))
        axes[0, 1].set_xticklabels(
            [day[:3] for day in dow_avg.dropna().index], rotation=45)
        axes[0, 1].grid(True, alpha=0.3)
    else:
        axes[0, 1].text(0.5, 0.5, 'Insufficient daily data',
                        ha='center', va='center', transform=axes[0, 1].transAxes)
        axes[0, 1].set_title('Day of Week Pattern', fontweight='bold')

    # Hourly pattern (if data has hourly granularity)
    if ts_df['hour'].nunique() > 1:
        hourly_avg = ts_df.groupby('hour')[value_col].mean()
        axes[1, 0].plot(hourly_avg.index, hourly_avg.values,
                        color=colors[0], marker='o', linewidth=2, markersize=4)
        axes[1, 0].set_title('Average by Hour', fontweight='bold')
        axes[1, 0].set_xlabel('Hour of Day')
        axes[1, 0].set_ylabel(f'Average {value_col}')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_xlim(0, 23)
    else:
        axes[1, 0].text(0.5, 0.5, 'No hourly variation', ha='center',
                        va='center', transform=axes[1, 0].transAxes)
        axes[1, 0].set_title('Hourly Pattern', fontweight='bold')

    # Yearly trend (if multiple years)
    if ts_df['year'].nunique() > 1:
        yearly_avg = ts_df.groupby('year')[value_col].mean()
        axes[1, 1].plot(yearly_avg.index, yearly_avg.values,
                        color=colors[1], marker='o', linewidth=2, markersize=6)
        axes[1, 1].set_title('Yearly Trend', fontweight='bold')
        axes[1, 1].set_xlabel('Year')
        axes[1, 1].set_ylabel(f'Average {value_col}')
        axes[1, 1].grid(True, alpha=0.3)
    else:
        axes[1, 1].text(0.5, 0.5, 'Single year data', ha='center',
                        va='center', transform=axes[1, 1].transAxes)
        axes[1, 1].set_title('Yearly Trend', fontweight='bold')

    plt.tight_layout()
    return apply_chart_theme(fig, f"Time Series Patterns: {value_col}")


def plot_rolling_statistics(df: pd.DataFrame, datetime_col: str, value_col: str,
                            window_sizes: List[int] = None) -> plt.Figure:
    """
    Create rolling statistics plots (moving averages, rolling std).

    Args:
        df (pd.DataFrame): Input dataframe
        datetime_col (str): Name of datetime column
        value_col (str): Name of value column
        window_sizes (List[int], optional): List of window sizes for rolling calculations

    Returns:
        plt.Figure: Matplotlib figure object
    """
    # Prepare data
    ts_df = df.copy()
    ts_df[datetime_col] = pd.to_datetime(ts_df[datetime_col], errors='coerce')
    ts_df = ts_df.dropna(subset=[datetime_col, value_col])
    ts_df = ts_df.sort_values(datetime_col)

    if len(ts_df) < 10:
        return _create_error_figure("Insufficient data for rolling statistics")

    if window_sizes is None:
        # Auto-determine window sizes based on data length
        data_length = len(ts_df)
        if data_length > 365:
            window_sizes = [7, 30, 90]  # Daily data: week, month, quarter
        elif data_length > 30:
            window_sizes = [3, 7, 14]   # Shorter periods
        else:
            window_sizes = [3, 5]       # Very short data

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    colors = get_color_palette(len(window_sizes) + 1,
                               palette_name=getattr(st.session_state, 'color_palette', 'Default (Husl)'))

    # Plot original data
    ax1.plot(ts_df[datetime_col], ts_df[value_col],
             color=colors[0], alpha=0.6, linewidth=1, label='Original')

    # Plot rolling means
    for i, window in enumerate(window_sizes):
        if window < len(ts_df):
            rolling_mean = ts_df[value_col].rolling(
                window=window, center=True).mean()
            ax1.plot(ts_df[datetime_col], rolling_mean,
                     color=colors[i+1], linewidth=2, label=f'{window}-period MA')

    ax1.set_title(f'Rolling Averages: {value_col}', fontweight='bold')
    ax1.set_xlabel('Date')
    ax1.set_ylabel(value_col)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Plot rolling standard deviation
    for i, window in enumerate(window_sizes):
        if window < len(ts_df):
            rolling_std = ts_df[value_col].rolling(
                window=window, center=True).std()
            ax2.plot(ts_df[datetime_col], rolling_std,
                     color=colors[i+1], linewidth=2, label=f'{window}-period Std')

    ax2.set_title(
        f'Rolling Standard Deviation: {value_col}', fontweight='bold')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Standard Deviation')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')

    plt.tight_layout()
    return apply_chart_theme(fig, f"Rolling Statistics: {value_col}")


def _create_error_figure(message: str) -> plt.Figure:
    """
    Create a figure displaying an error message.

    Args:
        message (str): Error message to display

    Returns:
        plt.Figure: Matplotlib figure with error message
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.text(0.5, 0.5, message, ha='center', va='center',
            fontsize=14, transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral", alpha=0.5))
    ax.axis('off')
    return apply_chart_theme(fig, "Time Series Analysis Error")


def analyze_time_series_stats(df: pd.DataFrame, datetime_col: str, value_col: str) -> Dict[str, Any]:
    """
    Calculate comprehensive time series statistics.

    Args:
        df (pd.DataFrame): Input dataframe
        datetime_col (str): Name of datetime column
        value_col (str): Name of value column

    Returns:
        dict: Dictionary containing time series statistics
    """
    # Prepare data
    ts_df = df.copy()
    ts_df[datetime_col] = pd.to_datetime(ts_df[datetime_col], errors='coerce')
    ts_df = ts_df.dropna(subset=[datetime_col, value_col])
    ts_df = ts_df.sort_values(datetime_col)

    if len(ts_df) == 0:
        return {'error': 'No valid data found'}

    stats = {
        'data_points': len(ts_df),
        'date_range': {
            'start': ts_df[datetime_col].min(),
            'end': ts_df[datetime_col].max(),
            'days': (ts_df[datetime_col].max() - ts_df[datetime_col].min()).days
        },
        'value_stats': {
            'mean': ts_df[value_col].mean(),
            'median': ts_df[value_col].median(),
            'std': ts_df[value_col].std(),
            'min': ts_df[value_col].min(),
            'max': ts_df[value_col].max(),
            'missing_count': ts_df[value_col].isnull().sum()
        }
    }

    # Calculate basic trend
    if len(ts_df) > 2:
        x = np.arange(len(ts_df))
        y = ts_df[value_col].fillna(ts_df[value_col].mean())
        slope, intercept = np.polyfit(x, y, 1)
        stats['trend'] = {
            'slope': slope,
            'direction': 'increasing' if slope > 0 else 'decreasing' if slope < 0 else 'stable',
            'change_per_day': slope * (len(ts_df) / stats['date_range']['days']) if stats['date_range']['days'] > 0 else 0
        }

    return stats
