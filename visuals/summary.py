"""
Data summary and overview visualizations.

Creates tables and charts showing data types, uniqueness, and basic statistics.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from style import apply_chart_theme


def plot_data_types_summary(df: pd.DataFrame) -> plt.Figure:
    """
    Create a visualization showing the distribution of data types.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        plt.Figure: Matplotlib figure object
    """
    dtype_counts = df.dtypes.value_counts()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Pie chart of data types
    colors = sns.color_palette("Set3", len(dtype_counts))
    wedges, texts, autotexts = ax1.pie(dtype_counts.values,
                                       labels=dtype_counts.index,
                                       autopct='%1.1f%%',
                                       colors=colors,
                                       startangle=90)

    ax1.set_title('Distribution of Data Types', fontweight='bold', fontsize=14)

    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_fontweight('bold')

    # Bar chart with counts
    bars = ax2.bar(range(len(dtype_counts)), dtype_counts.values,
                   color=colors)
    ax2.set_xlabel('Data Types', fontweight='bold')
    ax2.set_ylabel('Number of Columns', fontweight='bold')
    ax2.set_title('Column Count by Data Type', fontweight='bold', fontsize=14)
    ax2.set_xticks(range(len(dtype_counts)))
    ax2.set_xticklabels(dtype_counts.index, rotation=45, ha='right')

    # Add value labels on bars
    for bar, value in zip(bars, dtype_counts.values):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                 f'{int(value)}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    return apply_chart_theme(fig)


def plot_uniqueness_analysis(df: pd.DataFrame) -> plt.Figure:
    """
    Create a visualization showing uniqueness patterns across columns.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        plt.Figure: Matplotlib figure object
    """
    unique_counts = df.nunique()
    unique_percentages = (unique_counts / len(df)) * 100

    # Sort by uniqueness percentage
    sorted_data = pd.DataFrame({
        'Column': unique_counts.index,
        'Unique_Count': unique_counts.values,
        'Unique_Percentage': unique_percentages.values
    }).sort_values('Unique_Percentage', ascending=True)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12))

    # Top plot: Unique counts
    bars1 = ax1.barh(range(len(sorted_data)), sorted_data['Unique_Count'],
                     color=sns.color_palette("viridis", len(sorted_data)))

    ax1.set_xlabel('Number of Unique Values', fontweight='bold')
    ax1.set_ylabel('Columns', fontweight='bold')
    ax1.set_title('Unique Value Counts by Column',
                  fontweight='bold', fontsize=14)
    ax1.set_yticks(range(len(sorted_data)))
    ax1.set_yticklabels(sorted_data['Column'])

    # Add value labels
    for i, (bar, value) in enumerate(zip(bars1, sorted_data['Unique_Count'])):
        width = bar.get_width()
        ax1.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                 f'{int(value)}', ha='left', va='center', fontweight='bold')

    # Bottom plot: Unique percentages
    colors = ['red' if x > 80 else 'orange' if x > 50 else 'green'
              for x in sorted_data['Unique_Percentage']]

    bars2 = ax2.barh(range(len(sorted_data)), sorted_data['Unique_Percentage'],
                     color=colors, alpha=0.7)

    ax2.set_xlabel('Unique Values Percentage (%)', fontweight='bold')
    ax2.set_ylabel('Columns', fontweight='bold')
    ax2.set_title('Uniqueness Percentage by Column',
                  fontweight='bold', fontsize=14)
    ax2.set_yticks(range(len(sorted_data)))
    ax2.set_yticklabels(sorted_data['Column'])
    ax2.set_xlim(0, 100)

    # Add percentage labels
    for i, (bar, value) in enumerate(zip(bars2, sorted_data['Unique_Percentage'])):
        width = bar.get_width()
        ax2.text(width + 1, bar.get_y() + bar.get_height()/2,
                 f'{value:.1f}%', ha='left', va='center', fontweight='bold')

    # Add reference lines
    ax2.axvline(x=50, color='orange', linestyle='--', alpha=0.5, label='50%')
    ax2.axvline(x=80, color='red', linestyle='--', alpha=0.5, label='80%')
    ax2.legend()

    plt.tight_layout()
    return apply_chart_theme(fig)


def create_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a comprehensive summary table of the dataframe.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        pd.DataFrame: Summary statistics table
    """
    summary_data = []

    for col in df.columns:
        col_info = {
            'Column': col,
            'Data Type': str(df[col].dtype),
            'Non-Null Count': df[col].count(),
            'Null Count': df[col].isnull().sum(),
            'Null %': f"{(df[col].isnull().sum() / len(df)) * 100:.1f}%",
            'Unique Values': df[col].nunique(),
            'Unique %': f"{(df[col].nunique() / len(df)) * 100:.1f}%"
        }

        # Add type-specific information
        if pd.api.types.is_numeric_dtype(df[col]):
            col_info.update({
                'Mean': f"{df[col].mean():.2f}" if not df[col].isnull().all() else "N/A",
                'Std': f"{df[col].std():.2f}" if not df[col].isnull().all() else "N/A",
                'Min': f"{df[col].min():.2f}" if not df[col].isnull().all() else "N/A",
                'Max': f"{df[col].max():.2f}" if not df[col].isnull().all() else "N/A"
            })
        elif pd.api.types.is_object_dtype(df[col]) or pd.api.types.is_categorical_dtype(df[col]):
            most_common = df[col].mode()
            col_info.update({
                'Most Common': most_common.iloc[0] if not most_common.empty else "N/A",
                'Most Common Count': df[col].value_counts().iloc[0] if not df[col].empty else 0,
                'Avg Length': f"{df[col].astype(str).str.len().mean():.1f}" if not df[col].isnull().all() else "N/A"
            })

        summary_data.append(col_info)

    return pd.DataFrame(summary_data)


def plot_memory_usage(df: pd.DataFrame) -> plt.Figure:
    """
    Create a visualization showing memory usage by column.

    Args:
        df (pd.DataFrame): Input dataframe

    Returns:
        plt.Figure: Matplotlib figure object
    """
    memory_usage = df.memory_usage(deep=True)
    memory_usage = memory_usage.drop(
        'Index') if 'Index' in memory_usage.index else memory_usage
    memory_usage_mb = memory_usage / (1024 ** 2)  # Convert to MB

    # Sort by memory usage
    memory_usage_mb = memory_usage_mb.sort_values(ascending=False)

    fig, ax = plt.subplots(figsize=(12, 8))

    # Create horizontal bar chart
    bars = ax.barh(range(len(memory_usage_mb)), memory_usage_mb.values,
                   color=sns.color_palette("plasma", len(memory_usage_mb)))

    ax.set_xlabel('Memory Usage (MB)', fontweight='bold')
    ax.set_ylabel('Columns', fontweight='bold')
    ax.set_title('Memory Usage by Column', fontweight='bold', fontsize=14)
    ax.set_yticks(range(len(memory_usage_mb)))
    ax.set_yticklabels(memory_usage_mb.index)

    # Add value labels
    for i, (bar, value) in enumerate(zip(bars, memory_usage_mb.values)):
        width = bar.get_width()
        ax.text(width + width*0.01, bar.get_y() + bar.get_height()/2,
                f'{value:.2f} MB', ha='left', va='center', fontweight='bold')

    # Add total memory usage text
    total_memory = memory_usage_mb.sum()
    ax.text(0.02, 0.98, f'Total Memory: {total_memory:.2f} MB',
            transform=ax.transAxes, fontsize=12, fontweight='bold',
            bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.7))

    plt.tight_layout()
    return apply_chart_theme(fig)
