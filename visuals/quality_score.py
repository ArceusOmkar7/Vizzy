"""
Data Quality Visualization Functions for Vizzy

Creates charts and visualizations for data quality assessment.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

from style import get_color_palette


def create_quality_score_gauge(score: float, grade: str, palette_name: str = 'Default (Husl)') -> go.Figure:
    """Create a gauge chart for overall quality score."""
    colors = get_color_palette(4, palette_name)

    # Determine gauge color based on score
    if score >= 90:
        gauge_color = colors[0]  # Green
    elif score >= 80:
        gauge_color = colors[1]  # Blue
    elif score >= 70:
        gauge_color = colors[2]  # Orange
    else:
        gauge_color = colors[3]  # Red

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"Overall Quality Score<br><span style='font-size:0.8em;color:gray'>Grade: {grade}</span>"},
        delta={'reference': 80},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': gauge_color},
            'steps': [
                {'range': [0, 60], 'color': "lightgray"},
                {'range': [60, 80], 'color': "yellow"},
                {'range': [80, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        font={'size': 16}
    )

    return fig


def create_dimension_scores_chart(dimensions: Dict[str, Dict], palette_name: str = 'Default (Husl)') -> go.Figure:
    """Create horizontal bar chart for quality dimension scores."""
    dimension_names = list(dimensions.keys())
    scores = [dimensions[dim]['score'] for dim in dimension_names]

    # Capitalize dimension names
    display_names = [name.replace('_', ' ').title()
                     for name in dimension_names]

    colors = get_color_palette(len(dimension_names), palette_name)

    fig = go.Figure(data=[
        go.Bar(
            y=display_names,
            x=scores,
            orientation='h',
            marker_color=colors,
            text=[f"{score}%" for score in scores],
            textposition="inside",
            textfont=dict(color="white", size=12)
        )
    ])

    fig.update_layout(
        title="Quality Scores by Dimension",
        xaxis_title="Score (%)",
        yaxis_title="Quality Dimension",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(range=[0, 100])
    )

    return fig


def create_column_quality_heatmap(df: pd.DataFrame, palette_name: str = 'Default (Husl)') -> plt.Figure:
    """Create heatmap showing quality score for each column."""
    from utils.quality_engine import get_column_quality_details

    quality_df = get_column_quality_details(df)

    # Prepare data for heatmap
    heatmap_data = quality_df.set_index('Column')[['Quality Score']].T

    # Set up the plot
    plt.figure(figsize=(max(12, len(df.columns) * 0.5), 3))

    # Create heatmap
    colors = get_color_palette(256, palette_name)
    cmap = plt.matplotlib.colors.ListedColormap(colors)

    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt='.0f',
        cmap='RdYlGn',  # Red-Yellow-Green colormap for quality scores
        center=75,
        vmin=0,
        vmax=100,
        cbar_kws={'label': 'Quality Score'},
        linewidths=0.5
    )

    plt.title('Column Quality Scores', fontsize=14, fontweight='bold', pad=20)
    plt.xlabel('Columns', fontsize=12)
    plt.ylabel('')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    return plt.gcf()


def create_issues_summary_chart(dimensions: Dict[str, Dict], palette_name: str = 'Default (Husl)') -> go.Figure:
    """Create a summary chart of all identified issues."""
    all_issues = []
    dimension_labels = []

    for dim_name, dim_data in dimensions.items():
        issues = dim_data.get('issues', [])
        for issue in issues:
            all_issues.append(issue)
            dimension_labels.append(dim_name.replace('_', ' ').title())

    if not all_issues:
        # No issues found - show success message
        fig = go.Figure()
        fig.add_annotation(
            text="🎉 No major data quality issues detected!<br>Your dataset is in excellent condition.",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="green")
        )
        fig.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig

    # Create issues chart
    colors = get_color_palette(len(set(dimension_labels)), palette_name)
    color_map = {dim: colors[i] for i, dim in enumerate(set(dimension_labels))}

    issue_colors = [color_map[label] for label in dimension_labels]

    fig = go.Figure(data=[
        go.Bar(
            y=all_issues,
            x=[1] * len(all_issues),  # All bars same length
            orientation='h',
            marker_color=issue_colors,
            text=dimension_labels,
            textposition="inside",
            textfont=dict(color="white", size=10)
        )
    ])

    fig.update_layout(
        title="Identified Data Quality Issues",
        xaxis_title="",
        yaxis_title="Issues",
        height=max(300, len(all_issues) * 30),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(visible=False),
        showlegend=False
    )

    return fig


def create_missing_values_overview(df: pd.DataFrame, palette_name: str = 'Default (Husl)') -> go.Figure:
    """Create overview chart of missing values per column."""
    missing_counts = df.isnull().sum()
    missing_percentages = (missing_counts / len(df)) * 100

    # Filter to only columns with missing values
    missing_data = missing_percentages[missing_percentages > 0].sort_values(
        ascending=True)

    if len(missing_data) == 0:
        # No missing values
        fig = go.Figure()
        fig.add_annotation(
            text="✅ No missing values found in dataset!",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16, color="green")
        )
        fig.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig

    colors = get_color_palette(len(missing_data), palette_name)

    fig = go.Figure(data=[
        go.Bar(
            y=missing_data.index,
            x=missing_data.values,
            orientation='h',
            marker_color=colors,
            text=[f"{val:.1f}%" for val in missing_data.values],
            textposition="outside",
            textfont=dict(size=10)
        )
    ])

    fig.update_layout(
        title="Missing Values by Column",
        xaxis_title="Missing Percentage (%)",
        yaxis_title="Columns",
        height=max(300, len(missing_data) * 25),
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig


def create_data_types_distribution(df: pd.DataFrame, palette_name: str = 'Default (Husl)') -> go.Figure:
    """Create pie chart showing distribution of data types."""
    type_counts = df.dtypes.value_counts()

    # Map dtypes to more readable names
    type_mapping = {
        'object': 'Text/Categorical',
        'int64': 'Integer',
        'float64': 'Decimal',
        'datetime64[ns]': 'Date/Time',
        'bool': 'Boolean',
        'category': 'Categorical'
    }

    readable_types = [type_mapping.get(
        str(dtype), str(dtype)) for dtype in type_counts.index]
    colors = get_color_palette(len(type_counts), palette_name)

    fig = go.Figure(data=[go.Pie(
        labels=readable_types,
        values=type_counts.values,
        hole=.3,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='outside'
    )])

    fig.update_layout(
        title="Data Types Distribution",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig


def create_quality_recommendations_display(recommendations: List[str]) -> str:
    """Format quality recommendations for display."""
    if not recommendations:
        return "🎉 **Excellent!** No recommendations needed - your data quality is outstanding!"

    formatted_recommendations = []
    for i, rec in enumerate(recommendations, 1):
        formatted_recommendations.append(f"{i}. {rec}")

    return "\n".join(formatted_recommendations)


def create_detailed_issues_table(dimensions: Dict[str, Dict]) -> pd.DataFrame:
    """Create detailed table of all quality issues found."""
    issues_data = []

    for dim_name, dim_data in dimensions.items():
        dimension = dim_name.replace('_', ' ').title()
        score = dim_data['score']
        issues = dim_data.get('issues', [])
        details = dim_data.get('details', {})

        if not issues:
            issues_data.append({
                'Dimension': dimension,
                'Score': f"{score}%",
                'Status': '✅ Good',
                'Issues': 'No issues detected',
                'Details': 'All checks passed'
            })
        else:
            for issue in issues:
                # Extract relevant details for this issue
                issue_details = []
                if 'missing' in issue.lower() and 'worst_columns' in details:
                    worst_cols = details['worst_columns']
                    if worst_cols:
                        top_col = list(worst_cols.keys())[0]
                        issue_details.append(
                            f"Worst: {top_col} ({worst_cols[top_col]:.1f}%)")

                if 'outlier' in issue.lower() and 'outlier_columns' in details:
                    outlier_cols = details['outlier_columns']
                    if outlier_cols:
                        top_col = list(outlier_cols.keys())[0]
                        issue_details.append(
                            f"Worst: {top_col} ({outlier_cols[top_col]}% outliers)")

                if 'duplicate' in issue.lower() and 'duplicate_percentage' in details:
                    dup_pct = details['duplicate_percentage']
                    issue_details.append(f"Duplicate rate: {dup_pct}%")

                status = '⚠️ Warning' if score >= 70 else '❌ Critical'

                issues_data.append({
                    'Dimension': dimension,
                    'Score': f"{score}%",
                    'Status': status,
                    'Issues': issue,
                    'Details': '; '.join(issue_details) if issue_details else 'See full report for details'
                })

    return pd.DataFrame(issues_data)
