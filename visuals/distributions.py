"""
Distribution analysis and visualization functions.

Creates histograms, box plots, and other distribution visualizations.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import streamlit as st
from typing import List, Optional
from style import apply_chart_theme, get_color_palette


def plot_numeric_distributions(df: pd.DataFrame, columns: Optional[List[str]] = None,
                               bins: int = 30) -> plt.Figure:
    """
    Create histograms for numeric columns.

    Args:
        df (pd.DataFrame): Input dataframe
        columns (List[str], optional): Specific columns to plot. If None, plot all numeric columns
        bins (int): Number of bins for histograms

    Returns:
        plt.Figure: Matplotlib figure object
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if columns:
        numeric_cols = [col for col in columns if col in numeric_cols]

    if not numeric_cols:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'No numeric columns found for distribution analysis',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Numeric Distributions")

    # Calculate subplot layout
    n_cols = min(3, len(numeric_cols))
    n_rows = (len(numeric_cols) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 5, n_rows * 4))
    if n_rows == 1 and n_cols == 1:
        axes = [axes]
    elif n_rows == 1 or n_cols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()

    colors = get_color_palette(len(numeric_cols),
                               palette_name=getattr(st.session_state, 'color_palette', 'Default (Husl)'))

    for i, col in enumerate(numeric_cols):
        ax = axes[i]

        # Remove null values for plotting
        data = df[col].dropna()

        if len(data) == 0:
            ax.text(0.5, 0.5, f'No data available\nfor {col}',
                    ha='center', va='center', transform=ax.transAxes)
            ax.set_title(col, fontweight='bold')
            continue

        # Plot histogram with KDE
        ax.hist(data, bins=bins, alpha=0.7,
                color=colors[i], density=True, edgecolor='black')

        # Add KDE if data has variation
        if data.std() > 0:
            sns.kdeplot(data=data, ax=ax, color='red', linewidth=2)

        # Customize subplot
        ax.set_title(f'{col}', fontweight='bold')
        ax.set_xlabel('Value')
        ax.set_ylabel('Density')
        ax.grid(True, alpha=0.3)

        # Add statistics text
        stats_text = f'Mean: {data.mean():.2f}\nStd: {data.std():.2f}\nSkew: {data.skew():.2f}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
                verticalalignment='top', fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    # Hide unused subplots
    for i in range(len(numeric_cols), len(axes)):
        axes[i].axis('off')

    plt.tight_layout()
    return apply_chart_theme(fig, f"Distribution Analysis ({len(numeric_cols)} columns)")


def plot_box_plots(df: pd.DataFrame, columns: Optional[List[str]] = None) -> plt.Figure:
    """
    Create box plots for numeric columns to show outliers and quartiles.

    Args:
        df (pd.DataFrame): Input dataframe
        columns (List[str], optional): Specific columns to plot

    Returns:
        plt.Figure: Matplotlib figure object
    """
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if columns:
        numeric_cols = [col for col in columns if col in numeric_cols]

    if not numeric_cols:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, 'No numeric columns found for box plot analysis',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Box Plot Analysis")

    # Limit to reasonable number of columns for visibility
    if len(numeric_cols) > 8:
        numeric_cols = numeric_cols[:8]

    fig, ax = plt.subplots(figsize=(max(10, len(numeric_cols) * 1.5), 8))

    # Prepare data for box plot
    data_to_plot = []
    labels = []

    for col in numeric_cols:
        col_data = df[col].dropna()
        if len(col_data) > 0:
            data_to_plot.append(col_data)
            labels.append(col)

    if not data_to_plot:
        ax.text(0.5, 0.5, 'No data available for box plots',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Box Plot Analysis")

    # Create box plot
    box_plot = ax.boxplot(data_to_plot, labels=labels, patch_artist=True,
                          notch=True, showmeans=True)

    # Color the boxes
    colors = get_color_palette(len(data_to_plot),
                               palette_name=getattr(st.session_state, 'color_palette', 'Default (Husl)'))
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # Customize the plot
    ax.set_xlabel('Columns', fontweight='bold')
    ax.set_ylabel('Values', fontweight='bold')
    ax.set_title('Box Plot Analysis - Outliers and Quartiles',
                 fontweight='bold', fontsize=14)

    # Rotate x-axis labels if needed
    if len(labels) > 4:
        plt.xticks(rotation=45, ha='right')

    # Add grid
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    return apply_chart_theme(fig)


def plot_distribution_comparison(df: pd.DataFrame, column: str,
                                 group_by: Optional[str] = None) -> plt.Figure:
    """
    Compare distributions of a numeric column across groups or show detailed analysis.

    Args:
        df (pd.DataFrame): Input dataframe
        column (str): Column to analyze
        group_by (str, optional): Column to group by for comparison

    Returns:
        plt.Figure: Matplotlib figure object
    """
    if column not in df.columns:
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, f'Column "{column}" not found',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Distribution Comparison")

    if not pd.api.types.is_numeric_dtype(df[column]):
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.text(0.5, 0.5, f'Column "{column}" is not numeric',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Distribution Comparison")

    data = df[column].dropna()

    if group_by and group_by in df.columns:
        # Group comparison
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Overall distribution
        axes[0, 0].hist(data, bins=30, alpha=0.7,
                        density=True, edgecolor='black')
        if data.std() > 0:
            sns.kdeplot(data=data, ax=axes[0, 0], color='red', linewidth=2)
        axes[0, 0].set_title(
            f'Overall Distribution - {column}', fontweight='bold')
        axes[0, 0].set_xlabel('Value')
        axes[0, 0].set_ylabel('Density')

        # Box plot by group
        groups = df.groupby(group_by)[column].apply(
            lambda x: x.dropna()).reset_index(level=0, drop=True)
        unique_groups = df[group_by].unique()[:10]  # Limit to 10 groups

        group_data = [df[df[group_by] == group][column].dropna()
                      for group in unique_groups]
        group_data = [g for g in group_data if len(g) > 0]

        if group_data:
            axes[0, 1].boxplot(
                group_data, labels=unique_groups[:len(group_data)])
            axes[0, 1].set_title(f'{column} by {group_by}', fontweight='bold')
            axes[0, 1].set_xlabel(group_by)
            axes[0, 1].set_ylabel(column)
            plt.setp(axes[0, 1].xaxis.get_majorticklabels(),
                     rotation=45, ha='right')

        # Distribution by group (overlaid)
        colors = get_color_palette(len(unique_groups),
                                   palette_name=getattr(st.session_state, 'color_palette', 'Default (Husl)'))
        # Limit to 5 for readability
        for i, group in enumerate(unique_groups[:5]):
            group_data_single = df[df[group_by] == group][column].dropna()
            if len(group_data_single) > 0:
                axes[1, 0].hist(group_data_single, bins=20, alpha=0.5,
                                label=f'{group}', color=colors[i], density=True)

        axes[1, 0].set_title(
            f'Distribution Comparison by {group_by}', fontweight='bold')
        axes[1, 0].set_xlabel(column)
        axes[1, 0].set_ylabel('Density')
        axes[1, 0].legend()

        # Summary statistics table
        axes[1, 1].axis('off')
        summary_stats = df.groupby(group_by)[column].agg(
            ['count', 'mean', 'std', 'min', 'max']).round(2)
        table_data = summary_stats.head(10).values
        table = axes[1, 1].table(cellText=table_data,
                                 rowLabels=summary_stats.head(10).index,
                                 colLabels=['Count', 'Mean',
                                            'Std', 'Min', 'Max'],
                                 cellLoc='center',
                                 loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1.2, 1.5)
        axes[1, 1].set_title(
            f'Summary Statistics by {group_by}', fontweight='bold')

    else:
        # Detailed single column analysis
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))

        # Histogram with KDE
        axes[0, 0].hist(data, bins=30, alpha=0.7,
                        density=True, edgecolor='black')
        if data.std() > 0:
            sns.kdeplot(data=data, ax=axes[0, 0], color='red', linewidth=2)
        axes[0, 0].set_title(f'Distribution - {column}', fontweight='bold')
        axes[0, 0].set_xlabel('Value')
        axes[0, 0].set_ylabel('Density')

        # Q-Q plot for normality check
        from scipy import stats
        stats.probplot(data, dist="norm", plot=axes[0, 1])
        axes[0, 1].set_title(
            f'Q-Q Plot (Normality Check) - {column}', fontweight='bold')

        # Box plot
        axes[1, 0].boxplot([data], labels=[column])
        axes[1, 0].set_title(f'Box Plot - {column}', fontweight='bold')
        axes[1, 0].set_ylabel('Value')

        # Summary statistics
        axes[1, 1].axis('off')
        stats_text = f"""
        Count: {len(data):,}
        Mean: {data.mean():.3f}
        Median: {data.median():.3f}
        Std: {data.std():.3f}
        Min: {data.min():.3f}
        Max: {data.max():.3f}
        Skewness: {data.skew():.3f}
        Kurtosis: {data.kurtosis():.3f}
        
        Quartiles:
        Q1 (25%): {data.quantile(0.25):.3f}
        Q2 (50%): {data.quantile(0.50):.3f}
        Q3 (75%): {data.quantile(0.75):.3f}
        
        IQR: {data.quantile(0.75) - data.quantile(0.25):.3f}
        """
        axes[1, 1].text(0.1, 0.9, stats_text, transform=axes[1, 1].transAxes,
                        fontsize=11, verticalalignment='top', fontfamily='monospace')
        axes[1, 1].set_title(
            f'Summary Statistics - {column}', fontweight='bold')

    plt.tight_layout()
    return apply_chart_theme(fig)
