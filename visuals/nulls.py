"""
Null value visualization functions.

Creates bar charts and heatmaps to visualize missing data patterns.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import Tuple
from style import apply_chart_theme


def plot_null_bar_chart(df: pd.DataFrame) -> plt.Figure:
    """
    Create a bar chart showing null counts for each column.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        plt.Figure: Matplotlib figure object
    """
    null_counts = df.isnull().sum()
    null_counts = null_counts[null_counts > 0].sort_values(ascending=False)

    if null_counts.empty:
        # Create a simple message plot if no nulls
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'No missing values found!',
                ha='center', va='center', fontsize=16,
                transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        return apply_chart_theme(fig, "Missing Values Analysis")

    fig, ax = plt.subplots(figsize=(12, 6))

    bars = ax.bar(range(len(null_counts)), null_counts.values,
                  color=sns.color_palette("Reds_r", len(null_counts)))

    # Customize the plot
    ax.set_xlabel('Columns', fontweight='bold')
    ax.set_ylabel('Number of Missing Values', fontweight='bold')
    ax.set_xticks(range(len(null_counts)))
    ax.set_xticklabels(null_counts.index, rotation=45, ha='right')

    # Add value labels on bars
    for i, (bar, value) in enumerate(zip(bars, null_counts.values)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                f'{int(value)}', ha='center', va='bottom', fontweight='bold')

    # Add percentage on secondary y-axis
    ax2 = ax.twinx()
    percentages = (null_counts / len(df)) * 100
    ax2.plot(range(len(null_counts)), percentages.values, 'ro-', alpha=0.7)
    ax2.set_ylabel('Percentage Missing (%)', fontweight='bold', color='red')
    ax2.tick_params(axis='y', labelcolor='red')

    plt.tight_layout()
    return apply_chart_theme(fig, "Missing Values by Column")


def plot_null_heatmap(df: pd.DataFrame) -> plt.Figure:
    """
    Create a heatmap showing the pattern of missing values.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        plt.Figure: Matplotlib figure object
    """
    # Limit to columns with at least one null value
    null_cols = df.columns[df.isnull().any()].tolist()

    if not null_cols:
        # Create a simple message plot if no nulls
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'No missing values to display!',
                ha='center', va='center', fontsize=16,
                transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        return apply_chart_theme(fig, "Missing Values Heatmap")

    # Sample data if too large
    if len(df) > 1000:
        df_sample = df.sample(n=1000, random_state=42)
    else:
        df_sample = df

    # Create null matrix (1 = missing, 0 = present)
    null_matrix = df_sample[null_cols].isnull().astype(int)

    # Calculate figure size based on data
    fig_width = max(8, len(null_cols) * 0.5)
    fig_height = max(6, len(df_sample) * 0.01)
    fig_height = min(fig_height, 20)  # Cap the height

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    # Create heatmap
    sns.heatmap(null_matrix,
                cmap='Reds',
                cbar_kws={'label': 'Missing (1) vs Present (0)'},
                ax=ax,
                xticklabels=True,
                yticklabels=False)

    ax.set_xlabel('Columns', fontweight='bold')
    ax.set_ylabel('Rows (Sample)', fontweight='bold')

    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    return apply_chart_theme(fig, f"Missing Values Pattern ({len(df_sample)} rows)")


def plot_null_correlation(df: pd.DataFrame) -> plt.Figure:
    """
    Create a correlation heatmap of missing value patterns.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        plt.Figure: Matplotlib figure object
    """
    # Get columns with null values
    null_cols = df.columns[df.isnull().any()].tolist()

    if len(null_cols) < 2:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'Need at least 2 columns with missing values\nto show correlation patterns',
                ha='center', va='center', fontsize=14,
                transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        return apply_chart_theme(fig, "Missing Values Correlation")

    # Create correlation matrix of null patterns
    null_matrix = df[null_cols].isnull().astype(int)
    null_corr = null_matrix.corr()

    fig, ax = plt.subplots(figsize=(10, 8))

    # Create correlation heatmap
    mask = np.triu(np.ones_like(null_corr, dtype=bool))
    sns.heatmap(null_corr,
                mask=mask,
                annot=True,
                cmap='RdBu_r',
                center=0,
                square=True,
                fmt='.2f',
                cbar_kws={'label': 'Correlation Coefficient'},
                ax=ax)

    ax.set_xlabel('Columns', fontweight='bold')
    ax.set_ylabel('Columns', fontweight='bold')

    plt.tight_layout()
    return apply_chart_theme(fig, "Missing Values Correlation Matrix")
