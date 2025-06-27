"""
Correlation analysis and visualization functions.

Creates correlation heatmaps and relationship analysis between numeric variables.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Optional, Tuple
from style import apply_chart_theme


def plot_correlation_heatmap(df: pd.DataFrame, method: str = 'pearson',
                             annot: bool = True, figsize: Tuple[int, int] = (12, 10)) -> plt.Figure:
    """
    Create a correlation heatmap for numeric columns.

    Args:
        df (pd.DataFrame): Input dataframe
        method (str): Correlation method ('pearson', 'spearman', 'kendall')
        annot (bool): Whether to annotate correlation values
        figsize (tuple): Figure size

    Returns:
        plt.Figure: Matplotlib figure object
    """
    # Select only numeric columns
    numeric_df = df.select_dtypes(include=[np.number])

    if numeric_df.empty or numeric_df.shape[1] < 2:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'Need at least 2 numeric columns for correlation analysis',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Correlation Analysis")

    # Calculate correlation matrix
    corr_matrix = numeric_df.corr(method=method)

    # Create mask for upper triangle to show only half
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))

    fig, ax = plt.subplots(figsize=figsize)

    # Create heatmap
    sns.heatmap(corr_matrix,
                mask=mask,
                annot=annot,
                cmap='RdBu_r',
                center=0,
                square=True,
                fmt='.2f' if annot else None,
                cbar_kws={'label': f'{method.title()} Correlation Coefficient'},
                ax=ax,
                annot_kws={'size': 10})

    ax.set_title(f'{method.title()} Correlation Matrix',
                 fontweight='bold', fontsize=16)

    # Rotate labels for better readability
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)

    plt.tight_layout()
    return apply_chart_theme(fig)


def plot_correlation_strength_distribution(df: pd.DataFrame, method: str = 'pearson') -> plt.Figure:
    """
    Create a histogram showing the distribution of correlation strengths.

    Args:
        df (pd.DataFrame): Input dataframe
        method (str): Correlation method

    Returns:
        plt.Figure: Matplotlib figure object
    """
    numeric_df = df.select_dtypes(include=[np.number])

    if numeric_df.empty or numeric_df.shape[1] < 2:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'Need at least 2 numeric columns for correlation analysis',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Correlation Strength Distribution")

    # Calculate correlation matrix
    corr_matrix = numeric_df.corr(method=method)

    # Extract upper triangle (excluding diagonal)
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
    correlations = corr_matrix.where(mask).stack().dropna()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    # Histogram of correlation values
    ax1.hist(correlations, bins=30, alpha=0.7,
             edgecolor='black', color='skyblue')
    ax1.axvline(correlations.mean(), color='red', linestyle='--', linewidth=2,
                label=f'Mean: {correlations.mean():.3f}')
    ax1.axvline(correlations.median(), color='orange', linestyle='--', linewidth=2,
                label=f'Median: {correlations.median():.3f}')

    ax1.set_xlabel('Correlation Coefficient', fontweight='bold')
    ax1.set_ylabel('Frequency', fontweight='bold')
    ax1.set_title(
        f'Distribution of {method.title()} Correlations', fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Categorize correlations by strength
    strong_positive = (correlations >= 0.7).sum()
    moderate_positive = ((correlations >= 0.3) & (correlations < 0.7)).sum()
    weak_positive = ((correlations > 0.1) & (correlations < 0.3)).sum()
    negligible = ((correlations >= -0.1) & (correlations <= 0.1)).sum()
    weak_negative = ((correlations > -0.3) & (correlations <= -0.1)).sum()
    moderate_negative = ((correlations > -0.7) & (correlations <= -0.3)).sum()
    strong_negative = (correlations <= -0.7).sum()

    categories = ['Strong\nNegative\n(≤-0.7)', 'Moderate\nNegative\n(-0.7 to -0.3)',
                  'Weak\nNegative\n(-0.3 to -0.1)', 'Negligible\n(-0.1 to 0.1)',
                  'Weak\nPositive\n(0.1 to 0.3)', 'Moderate\nPositive\n(0.3 to 0.7)',
                  'Strong\nPositive\n(≥0.7)']

    counts = [strong_negative, moderate_negative, weak_negative, negligible,
              weak_positive, moderate_positive, strong_positive]

    colors = ['darkred', 'red', 'lightcoral',
              'lightgray', 'lightblue', 'blue', 'darkblue']

    bars = ax2.bar(categories, counts, color=colors,
                   alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Correlation Strength Category', fontweight='bold')
    ax2.set_ylabel('Number of Pairs', fontweight='bold')
    ax2.set_title('Correlation Strength Categories', fontweight='bold')
    ax2.tick_params(axis='x', rotation=45)

    # Add count labels on bars
    for bar, count in zip(bars, counts):
        if count > 0:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                     f'{int(count)}', ha='center', va='bottom', fontweight='bold')

    plt.tight_layout()
    return apply_chart_theme(fig)


def plot_top_correlations(df: pd.DataFrame, method: str = 'pearson',
                          top_n: int = 10, min_correlation: float = 0.1) -> plt.Figure:
    """
    Plot the top N strongest correlations (by absolute value).

    Args:
        df (pd.DataFrame): Input dataframe
        method (str): Correlation method
        top_n (int): Number of top correlations to show
        min_correlation (float): Minimum correlation threshold

    Returns:
        plt.Figure: Matplotlib figure object
    """
    numeric_df = df.select_dtypes(include=[np.number])

    if numeric_df.empty or numeric_df.shape[1] < 2:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'Need at least 2 numeric columns for correlation analysis',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Top Correlations")

    # Calculate correlation matrix
    corr_matrix = numeric_df.corr(method=method)

    # Extract upper triangle (excluding diagonal)
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)

    # Get correlation pairs
    correlation_pairs = []
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            correlation_pairs.append({
                'Variable 1': corr_matrix.columns[i],
                'Variable 2': corr_matrix.columns[j],
                'Correlation': corr_matrix.iloc[i, j]
            })

    # Convert to DataFrame and sort
    corr_df = pd.DataFrame(correlation_pairs)
    corr_df['Abs_Correlation'] = corr_df['Correlation'].abs()

    # Filter by minimum correlation and get top N
    filtered_corr = corr_df[corr_df['Abs_Correlation'] >= min_correlation]
    top_correlations = filtered_corr.nlargest(top_n, 'Abs_Correlation')

    if top_correlations.empty:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, f'No correlations found above threshold {min_correlation}',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Top Correlations")

    # Create labels for the pairs
    pair_labels = [f"{row['Variable 1']}\nvs\n{row['Variable 2']}"
                   for _, row in top_correlations.iterrows()]

    fig, ax = plt.subplots(figsize=(14, 8))

    # Color bars based on positive/negative correlation
    colors = ['red' if corr <
              0 else 'blue' for corr in top_correlations['Correlation']]

    bars = ax.barh(range(len(top_correlations)), top_correlations['Correlation'],
                   color=colors, alpha=0.7, edgecolor='black')

    ax.set_xlabel(f'{method.title()} Correlation Coefficient',
                  fontweight='bold')
    ax.set_ylabel('Variable Pairs', fontweight='bold')
    ax.set_title(f'Top {len(top_correlations)} Strongest Correlations',
                 fontweight='bold', fontsize=14)
    ax.set_yticks(range(len(top_correlations)))
    ax.set_yticklabels(pair_labels)

    # Add correlation value labels
    for i, (bar, corr) in enumerate(zip(bars, top_correlations['Correlation'])):
        width = bar.get_width()
        label_x = width + (0.01 if width >= 0 else -0.01)
        ha = 'left' if width >= 0 else 'right'
        ax.text(label_x, bar.get_y() + bar.get_height()/2, f'{corr:.3f}',
                ha=ha, va='center', fontweight='bold')

    # Add reference lines
    ax.axvline(x=0, color='black', linestyle='-', alpha=0.3)
    ax.axvline(x=0.3, color='green', linestyle='--',
               alpha=0.5, label='Moderate (±0.3)')
    ax.axvline(x=-0.3, color='green', linestyle='--', alpha=0.5)
    ax.axvline(x=0.7, color='orange', linestyle='--',
               alpha=0.5, label='Strong (±0.7)')
    ax.axvline(x=-0.7, color='orange', linestyle='--', alpha=0.5)

    ax.legend()
    ax.grid(True, alpha=0.3, axis='x')

    plt.tight_layout()
    return apply_chart_theme(fig)


def plot_correlation_network(df: pd.DataFrame, method: str = 'pearson',
                             threshold: float = 0.5) -> plt.Figure:
    """
    Create a network-style visualization of strong correlations.

    Args:
        df (pd.DataFrame): Input dataframe
        method (str): Correlation method
        threshold (float): Minimum correlation strength to show

    Returns:
        plt.Figure: Matplotlib figure object
    """
    numeric_df = df.select_dtypes(include=[np.number])

    if numeric_df.empty or numeric_df.shape[1] < 2:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, 'Need at least 2 numeric columns for correlation network',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Correlation Network")

    # Calculate correlation matrix
    corr_matrix = numeric_df.corr(method=method)

    # Filter correlations by threshold
    strong_corr = corr_matrix.abs() >= threshold

    # Check if any strong correlations exist
    mask = np.triu(np.ones_like(strong_corr, dtype=bool), k=1)
    if not strong_corr.where(mask).any().any():
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.text(0.5, 0.5, f'No correlations found above threshold {threshold}',
                ha='center', va='center', fontsize=14, transform=ax.transAxes)
        ax.axis('off')
        return apply_chart_theme(fig, "Correlation Network")

    fig, ax = plt.subplots(figsize=(12, 12))

    # Create circular layout for variables
    n_vars = len(corr_matrix.columns)
    angles = np.linspace(0, 2*np.pi, n_vars, endpoint=False)

    # Position variables in a circle
    positions = {}
    radius = 3
    for i, var in enumerate(corr_matrix.columns):
        x = radius * np.cos(angles[i])
        y = radius * np.sin(angles[i])
        positions[var] = (x, y)

    # Draw edges for strong correlations
    for i in range(len(corr_matrix.columns)):
        for j in range(i+1, len(corr_matrix.columns)):
            var1 = corr_matrix.columns[i]
            var2 = corr_matrix.columns[j]
            correlation = corr_matrix.iloc[i, j]

            if abs(correlation) >= threshold:
                x1, y1 = positions[var1]
                x2, y2 = positions[var2]

                # Line width based on correlation strength
                width = abs(correlation) * 5

                # Color based on positive/negative
                color = 'red' if correlation < 0 else 'blue'
                alpha = min(0.8, abs(correlation))

                ax.plot([x1, x2], [y1, y2], color=color, linewidth=width,
                        alpha=alpha, solid_capstyle='round')

                # Add correlation value at midpoint
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                ax.text(mid_x, mid_y, f'{correlation:.2f}',
                        ha='center', va='center', fontsize=8,
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))

    # Draw nodes for variables
    for var, (x, y) in positions.items():
        ax.scatter(x, y, s=500, c='lightblue',
                   edgecolors='black', linewidth=2, zorder=5)
        ax.text(x, y, var, ha='center', va='center',
                fontweight='bold', fontsize=10, zorder=6)

    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(
        f'Correlation Network (|r| ≥ {threshold})', fontweight='bold', fontsize=16)

    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], color='blue', lw=3, label='Positive Correlation'),
        plt.Line2D([0], [0], color='red', lw=3, label='Negative Correlation'),
        plt.Line2D([0], [0], color='gray', lw=1,
                   label=f'Line width ∝ |correlation|')
    ]
    ax.legend(handles=legend_elements,
              loc='upper right', bbox_to_anchor=(1, 1))

    return apply_chart_theme(fig)
