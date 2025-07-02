"""
Categorical data visualization functions.

Creates value count charts, frequency analysis, and categorical data insights.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import streamlit as st
from typing import List, Optional, Tuple
from style import apply_chart_theme, get_color_palette


def plot_categorical_counts(df: pd.DataFrame, columns: Optional[List[str]] = None,
                            top_k: int = 10, min_frequency: int = 1) -> plt.Figure:
    """
    Create bar charts showing value counts for categorical columns.

    Args:
        df (pd.DataFrame): Input dataframe
        columns (List[str], optional): Specific columns to plot
        top_k (int): Number of top categories to show per column
        min_frequency (int): Minimum frequency to include a category

    Returns:
        plt.Figure: Matplotlib figure object
    """
    # Get categorical columns
    categorical_cols = df.select_dtypes(
        include=['object', 'category']).columns.tolist()

    if columns:
        categorical_cols = [col for col in columns if col in categorical_cols]

    if not categorical_cols:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'No categorical columns found for analysis',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Categorical Analysis")

    # Limit to reasonable number of columns
    if len(categorical_cols) > 6:
        categorical_cols = categorical_cols[:6]

    # Calculate subplot layout
    n_cols = min(2, len(categorical_cols))
    n_rows = (len(categorical_cols) + n_cols - 1) // n_cols

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 8, n_rows * 6))
    if n_rows == 1 and n_cols == 1:
        axes = [axes]
    elif n_rows == 1 or n_cols == 1:
        axes = axes.flatten()
    else:
        axes = axes.flatten()

    colors = get_color_palette(top_k,
                               palette_name=getattr(st.session_state, 'color_palette', 'Default (Husl)'))

    for i, col in enumerate(categorical_cols):
        ax = axes[i]

        # Get value counts
        value_counts = df[col].value_counts()

        # Filter by minimum frequency
        value_counts = value_counts[value_counts >= min_frequency]

        if value_counts.empty:
            ax.text(0.5, 0.5, f'No values above\nminimum frequency ({min_frequency})',
                    ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f'{col}', fontweight='bold')
            continue

        # Take top K values
        top_values = value_counts.head(top_k)

        # Create bar plot
        bars = ax.bar(range(len(top_values)), top_values.values,
                      color=colors[:len(top_values)], alpha=0.8, edgecolor='black')

        # Customize plot
        ax.set_title(f'{col} (Top {len(top_values)})',
                     fontweight='bold', fontsize=12)
        ax.set_xlabel('Categories')
        ax.set_ylabel('Count')
        ax.set_xticks(range(len(top_values)))
        ax.set_xticklabels(top_values.index, rotation=45, ha='right')

        # Add value labels on bars
        for bar, value in zip(bars, top_values.values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{int(value)}', ha='center', va='bottom', fontweight='bold', fontsize=9)

        # Add percentage labels
        total = df[col].count()
        for j, (bar, value) in enumerate(zip(bars, top_values.values)):
            percentage = (value / total) * 100
            ax.text(bar.get_x() + bar.get_width()/2., height/2,
                    f'{percentage:.1f}%', ha='center', va='center',
                    fontweight='bold', fontsize=8, color='white')

        ax.grid(True, alpha=0.3, axis='y')

    # Hide unused subplots
    for i in range(len(categorical_cols), len(axes)):
        axes[i].axis('off')

    plt.tight_layout()
    return apply_chart_theme(fig, f"Categorical Value Counts ({len(categorical_cols)} columns)")


def plot_category_distribution_pie(df: pd.DataFrame, column: str,
                                   top_k: int = 8, others_threshold: float = 0.02) -> plt.Figure:
    """
    Create a pie chart for a specific categorical column.

    Args:
        df (pd.DataFrame): Input dataframe
        column (str): Column to analyze
        top_k (int): Number of top categories to show individually
        others_threshold (float): Minimum percentage to show category individually

    Returns:
        plt.Figure: Matplotlib figure object
    """
    if column not in df.columns:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, f'Column "{column}" not found',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Category Distribution")

    value_counts = df[column].value_counts()
    total_count = value_counts.sum()

    # Calculate percentages
    percentages = value_counts / total_count

    # Group small categories into "Others"
    main_categories = percentages[percentages >= others_threshold].head(top_k)
    others_percentage = percentages[percentages < others_threshold].sum()

    if len(main_categories) < len(percentages):
        others_percentage += percentages.iloc[top_k:].sum()

    # Prepare data for pie chart
    if others_percentage > 0:
        plot_data = main_categories.copy()
        plot_data['Others'] = others_percentage
    else:
        plot_data = main_categories

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Pie chart
    colors = get_color_palette(len(plot_data),
                               palette_name=getattr(st.session_state, 'color_palette', 'Default (Husl)'))
    wedges, texts, autotexts = ax1.pie(plot_data.values,
                                       labels=plot_data.index,
                                       autopct='%1.1f%%',
                                       colors=colors,
                                       startangle=90,
                                       explode=[0.05 if i == 0 else 0 for i in range(len(plot_data))])

    ax1.set_title(f'Distribution of {column}', fontweight='bold', fontsize=14)

    # Make percentage text bold and larger
    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_fontsize(10)

    # Bar chart for exact counts
    bars = ax2.bar(range(len(plot_data)), plot_data.values * total_count,
                   color=colors, alpha=0.8, edgecolor='black')

    ax2.set_xlabel('Categories', fontweight='bold')
    ax2.set_ylabel('Count', fontweight='bold')
    ax2.set_title(f'Counts for {column}', fontweight='bold', fontsize=14)
    ax2.set_xticks(range(len(plot_data)))
    ax2.set_xticklabels(plot_data.index, rotation=45, ha='right')

    # Add value labels on bars
    for bar, value in zip(bars, plot_data.values * total_count):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                 f'{int(value)}', ha='center', va='bottom', fontweight='bold')

    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    return apply_chart_theme(fig)


def plot_categorical_relationship(df: pd.DataFrame, cat_col1: str, cat_col2: str,
                                  normalize: bool = True) -> plt.Figure:
    """
    Create a heatmap showing the relationship between two categorical variables.

    Args:
        df (pd.DataFrame): Input dataframe
        cat_col1 (str): First categorical column
        cat_col2 (str): Second categorical column
        normalize (bool): Whether to show percentages instead of counts

    Returns:
        plt.Figure: Matplotlib figure object
    """
    if cat_col1 not in df.columns or cat_col2 not in df.columns:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, f'One or both columns not found:\n{cat_col1}, {cat_col2}',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Categorical Relationship")

    # Create cross-tabulation
    crosstab = pd.crosstab(df[cat_col1], df[cat_col2])

    if normalize:
        # Normalize by row to show percentages
        crosstab_pct = crosstab.div(crosstab.sum(axis=1), axis=0) * 100
        crosstab_plot = crosstab_pct
        fmt = '.1f'
        cbar_label = 'Percentage (%)'
    else:
        crosstab_plot = crosstab
        fmt = 'd'
        cbar_label = 'Count'

    # Limit size if too large
    if crosstab_plot.shape[0] > 20:
        crosstab_plot = crosstab_plot.head(20)
    if crosstab_plot.shape[1] > 20:
        crosstab_plot = crosstab_plot.iloc[:, :20]

    fig, ax = plt.subplots(figsize=(max(8, crosstab_plot.shape[1] * 0.6),
                                    max(6, crosstab_plot.shape[0] * 0.4)))

    # Create heatmap
    sns.heatmap(crosstab_plot,
                annot=True,
                fmt=fmt,
                cmap='Blues',
                cbar_kws={'label': cbar_label},
                ax=ax)

    ax.set_xlabel(cat_col2, fontweight='bold')
    ax.set_ylabel(cat_col1, fontweight='bold')
    title = f'Relationship: {cat_col1} vs {cat_col2}'
    if normalize:
        title += ' (Row Percentages)'
    ax.set_title(title, fontweight='bold', fontsize=14)

    # Rotate labels for better readability
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    plt.tight_layout()
    return apply_chart_theme(fig)


def plot_categorical_summary_table(df: pd.DataFrame, columns: Optional[List[str]] = None) -> pd.DataFrame:
    """
    Create a summary table for categorical columns.

    Args:
        df (pd.DataFrame): Input dataframe
        columns (List[str], optional): Specific columns to analyze

    Returns:
        pd.DataFrame: Summary table
    """
    categorical_cols = df.select_dtypes(
        include=['object', 'category']).columns.tolist()

    if columns:
        categorical_cols = [col for col in columns if col in categorical_cols]

    if not categorical_cols:
        return pd.DataFrame({'Message': ['No categorical columns found']})

    summary_data = []

    for col in categorical_cols:
        value_counts = df[col].value_counts()

        summary_info = {
            'Column': col,
            'Total_Count': df[col].count(),
            'Null_Count': df[col].isnull().sum(),
            'Unique_Categories': df[col].nunique(),
            'Most_Frequent': value_counts.index[0] if not value_counts.empty else 'N/A',
            'Most_Frequent_Count': value_counts.iloc[0] if not value_counts.empty else 0,
            'Most_Frequent_Pct': f"{(value_counts.iloc[0] / df[col].count() * 100):.1f}%" if not value_counts.empty else 'N/A',
            'Least_Frequent': value_counts.index[-1] if len(value_counts) > 1 else 'N/A',
            'Least_Frequent_Count': value_counts.iloc[-1] if len(value_counts) > 1 else 0,
            'Entropy': calculate_entropy(value_counts),
        }

        # Add information about category distribution
        if len(value_counts) > 1:
            # Check if distribution is uniform
            expected_count = len(df) / len(value_counts)
            chi_square = sum((count - expected_count) ** 2 /
                             expected_count for count in value_counts)
            summary_info['Uniformity_Score'] = f"{(1 / (1 + chi_square / len(value_counts))):.3f}"
        else:
            summary_info['Uniformity_Score'] = "1.000"

        summary_data.append(summary_info)

    return pd.DataFrame(summary_data)


def calculate_entropy(value_counts: pd.Series) -> float:
    """
    Calculate Shannon entropy for a categorical distribution.

    Args:
        value_counts (pd.Series): Value counts for categories

    Returns:
        float: Shannon entropy
    """
    if len(value_counts) <= 1:
        return 0.0

    # Calculate probabilities
    probabilities = value_counts / value_counts.sum()

    # Calculate entropy
    entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)

    return entropy


def plot_categorical_diversity(df: pd.DataFrame, columns: Optional[List[str]] = None) -> plt.Figure:
    """
    Plot diversity metrics for categorical columns.

    Args:
        df (pd.DataFrame): Input dataframe
        columns (List[str], optional): Specific columns to analyze

    Returns:
        plt.Figure: Matplotlib figure object
    """
    categorical_cols = df.select_dtypes(
        include=['object', 'category']).columns.tolist()

    if columns:
        categorical_cols = [col for col in columns if col in categorical_cols]

    if not categorical_cols:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'No categorical columns found for diversity analysis',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Categorical Diversity")

    # Calculate diversity metrics
    diversity_data = []
    for col in categorical_cols:
        value_counts = df[col].value_counts()
        diversity_data.append({
            'Column': col,
            'Unique_Categories': len(value_counts),
            'Entropy': calculate_entropy(value_counts),
            'Gini_Impurity': calculate_gini_impurity(value_counts),
            'Simpson_Index': calculate_simpson_index(value_counts)
        })

    diversity_df = pd.DataFrame(diversity_data)

    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # Unique categories count
    bars1 = axes[0, 0].bar(diversity_df['Column'], diversity_df['Unique_Categories'],
                           color='skyblue', alpha=0.8, edgecolor='black')
    axes[0, 0].set_title('Number of Unique Categories', fontweight='bold')
    axes[0, 0].set_ylabel('Count')
    axes[0, 0].tick_params(axis='x', rotation=45)

    for bar, value in zip(bars1, diversity_df['Unique_Categories']):
        height = bar.get_height()
        axes[0, 0].text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{int(value)}', ha='center', va='bottom', fontweight='bold')

    # Entropy
    bars2 = axes[0, 1].bar(diversity_df['Column'], diversity_df['Entropy'],
                           color='lightgreen', alpha=0.8, edgecolor='black')
    axes[0, 1].set_title(
        'Shannon Entropy (Information Content)', fontweight='bold')
    axes[0, 1].set_ylabel('Entropy')
    axes[0, 1].tick_params(axis='x', rotation=45)

    for bar, value in zip(bars2, diversity_df['Entropy']):
        height = bar.get_height()
        axes[0, 1].text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:.2f}', ha='center', va='bottom', fontweight='bold')

    # Gini Impurity
    bars3 = axes[1, 0].bar(diversity_df['Column'], diversity_df['Gini_Impurity'],
                           color='lightcoral', alpha=0.8, edgecolor='black')
    axes[1, 0].set_title('Gini Impurity', fontweight='bold')
    axes[1, 0].set_ylabel('Gini Impurity')
    axes[1, 0].tick_params(axis='x', rotation=45)

    for bar, value in zip(bars3, diversity_df['Gini_Impurity']):
        height = bar.get_height()
        axes[1, 0].text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:.3f}', ha='center', va='bottom', fontweight='bold')

    # Simpson Index
    bars4 = axes[1, 1].bar(diversity_df['Column'], diversity_df['Simpson_Index'],
                           color='gold', alpha=0.8, edgecolor='black')
    axes[1, 1].set_title('Simpson Diversity Index', fontweight='bold')
    axes[1, 1].set_ylabel('Simpson Index')
    axes[1, 1].tick_params(axis='x', rotation=45)

    for bar, value in zip(bars4, diversity_df['Simpson_Index']):
        height = bar.get_height()
        axes[1, 1].text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                        f'{value:.3f}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    return apply_chart_theme(fig, "Categorical Diversity Analysis")


def calculate_gini_impurity(value_counts: pd.Series) -> float:
    """
    Calculate Gini impurity for a categorical distribution.

    Args:
        value_counts (pd.Series): Value counts for categories

    Returns:
        float: Gini impurity
    """
    if len(value_counts) <= 1:
        return 0.0

    total = value_counts.sum()
    probabilities = value_counts / total

    gini = 1 - sum(p ** 2 for p in probabilities)
    return gini


def calculate_simpson_index(value_counts: pd.Series) -> float:
    """
    Calculate Simpson diversity index for a categorical distribution.

    Args:
        value_counts (pd.Series): Value counts for categories

    Returns:
        float: Simpson diversity index
    """
    if len(value_counts) <= 1:
        return 0.0

    total = value_counts.sum()
    simpson = sum(count * (count - 1)
                  for count in value_counts) / (total * (total - 1))

    # Return Simpson diversity index (1 - Simpson's lambda)
    return 1 - simpson
