"""
Data Preprocessing Suggestions Visualization Functions for Vizzy

Creates charts and visualizations for preprocessing recommendations.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import streamlit as st
from typing import Dict, List, Any, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

from style import get_color_palette


def create_priority_chart(priorities: List[Tuple[str, float]], palette_name: str = 'Default (Husl)') -> go.Figure:
    """Create horizontal bar chart showing preprocessing priorities."""
    if not priorities:
        fig = go.Figure()
        fig.add_annotation(
            text="🎉 No preprocessing issues detected!<br>Your data is ready for analysis.",
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

    categories, scores = zip(*priorities)
    colors = get_color_palette(len(categories), palette_name)

    # Color-code by priority level
    priority_colors = []
    for score in scores:
        if score >= 70:
            priority_colors.append('#d32f2f')  # Red - Critical
        elif score >= 50:
            priority_colors.append('#f57c00')  # Orange - High
        elif score >= 30:
            priority_colors.append('#fbc02d')  # Yellow - Medium
        else:
            priority_colors.append('#388e3c')  # Green - Low

    fig = go.Figure(data=[
        go.Bar(
            y=categories,
            x=scores,
            orientation='h',
            marker_color=priority_colors,
            text=[f"{score:.0f}" for score in scores],
            textposition="inside",
            textfont=dict(color="white", size=12)
        )
    ])

    fig.update_layout(
        title="Preprocessing Priorities",
        xaxis_title="Priority Score",
        yaxis_title="Category",
        height=max(300, len(categories) * 40),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(range=[0, 100])
    )

    return fig


def create_summary_gauge(summary: Dict[str, Any], palette_name: str = 'Default (Husl)') -> go.Figure:
    """Create gauge showing overall preprocessing urgency."""
    urgency_scores = {
        'Low': 20,
        'Medium': 60,
        'High': 90
    }

    score = urgency_scores.get(summary['urgency'], 20)

    # Determine gauge color
    if score >= 80:
        gauge_color = '#d32f2f'  # Red
    elif score >= 50:
        gauge_color = '#f57c00'  # Orange
    else:
        gauge_color = '#388e3c'  # Green

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={
            'text': f"Preprocessing Urgency<br><span style='font-size:0.8em;color:gray'>{summary['urgency']} Priority</span>"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': gauge_color},
            'steps': [
                {'range': [0, 30], 'color': "lightgreen"},
                {'range': [30, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "lightcoral"}
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


def create_category_breakdown_chart(suggestions: Dict[str, Any], palette_name: str = 'Default (Husl)') -> go.Figure:
    """Create stacked bar chart showing issues by category."""
    categories = []
    issue_counts = []
    priority_scores = []

    for category, data in suggestions.items():
        if isinstance(data, dict) and 'suggestions' in data:
            category_name = category.replace('_', ' ').title()
            if category_name not in ['Priorities', 'Summary']:
                categories.append(category_name)

                # Count actual issues (not just "no issues" messages)
                suggestion_list = data['suggestions']
                actual_issues = len([s for s in suggestion_list if not s.startswith(
                    '✅') and not s.startswith('ℹ️')])
                issue_counts.append(actual_issues)
                priority_scores.append(data.get('priority', 0))

    if not categories or sum(issue_counts) == 0:
        fig = go.Figure()
        fig.add_annotation(
            text="📊 No preprocessing issues by category",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(
            height=200,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        return fig

    colors = get_color_palette(len(categories), palette_name)

    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=issue_counts,
            marker_color=colors,
            text=issue_counts,
            textposition="outside",
            textfont=dict(size=10)
        )
    ])

    fig.update_layout(
        title="Issues Count by Category",
        xaxis_title="Preprocessing Category",
        yaxis_title="Number of Issues",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(tickangle=45)
    )

    return fig


def create_missing_values_strategy_chart(missing_strategies: Dict[str, Any], palette_name: str = 'Default (Husl)') -> go.Figure:
    """Create chart showing missing value handling strategies."""
    if not missing_strategies:
        fig = go.Figure()
        fig.add_annotation(
            text="✅ No missing values to handle",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=14, color="green")
        )
        fig.update_layout(height=200)
        return fig

    columns = list(missing_strategies.keys())
    missing_percentages = [missing_strategies[col]
                           ['missing_percentage'] for col in columns]

    colors = get_color_palette(len(columns), palette_name)

    fig = go.Figure(data=[
        go.Bar(
            x=columns,
            y=missing_percentages,
            marker_color=colors,
            text=[f"{pct:.1f}%" for pct in missing_percentages],
            textposition="outside",
            textfont=dict(size=10)
        )
    ])

    fig.update_layout(
        title="Missing Values by Column",
        xaxis_title="Columns",
        yaxis_title="Missing Percentage (%)",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(tickangle=45)
    )

    return fig


def create_outlier_analysis_chart(outlier_strategies: Dict[str, Any], palette_name: str = 'Default (Husl)') -> go.Figure:
    """Create chart showing outlier analysis results."""
    if not outlier_strategies:
        fig = go.Figure()
        fig.add_annotation(
            text="✅ No significant outliers detected",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=14, color="green")
        )
        fig.update_layout(height=200)
        return fig

    columns = list(outlier_strategies.keys())
    outlier_percentages = [outlier_strategies[col]
                           ['outlier_percentage'] for col in columns]

    colors = get_color_palette(len(columns), palette_name)

    fig = go.Figure(data=[
        go.Bar(
            x=columns,
            y=outlier_percentages,
            marker_color=colors,
            text=[f"{pct:.1f}%" for pct in outlier_percentages],
            textposition="outside",
            textfont=dict(size=10)
        )
    ])

    fig.update_layout(
        title="Outlier Percentage by Column",
        xaxis_title="Columns",
        yaxis_title="Outlier Percentage (%)",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(tickangle=45)
    )

    return fig


def create_encoding_strategy_pie(encoding_strategies: Dict[str, Any], palette_name: str = 'Default (Husl)') -> go.Figure:
    """Create pie chart showing recommended encoding strategies."""
    if not encoding_strategies:
        fig = go.Figure()
        fig.add_annotation(
            text="ℹ️ No categorical columns to encode",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=14)
        )
        fig.update_layout(height=200)
        return fig

    strategy_counts = {}
    for col, data in encoding_strategies.items():
        strategy = data['strategy'].split(' (')[0]  # Get main strategy name
        strategy_counts[strategy] = strategy_counts.get(strategy, 0) + 1

    labels = list(strategy_counts.keys())
    values = list(strategy_counts.values())
    colors = get_color_palette(len(labels), palette_name)

    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=colors,
        textinfo='label+value',
        textposition='outside'
    )])

    fig.update_layout(
        title="Recommended Encoding Strategies",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig


def create_memory_optimization_chart(optimization_data: Dict[str, Any], palette_name: str = 'Default (Husl)') -> go.Figure:
    """Create chart showing potential memory savings."""
    memory_savings = optimization_data.get('memory_savings', 0)
    column_strategies = optimization_data.get('column_strategies', {})

    if memory_savings == 0 or not column_strategies:
        fig = go.Figure()
        fig.add_annotation(
            text="✅ Data types already optimized",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=14, color="green")
        )
        fig.update_layout(height=200)
        return fig

    # Create gauge for memory savings
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=memory_savings,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Potential Memory Savings (MB)"},
        delta={'reference': 0},
        gauge={
            'axis': {'range': [None, memory_savings * 2]},
            'bar': {'color': "#2196f3"},
            'steps': [
                {'range': [0, memory_savings * 0.5], 'color': "lightgray"},
                {'range': [memory_savings * 0.5,
                           memory_savings * 1.5], 'color': "lightblue"}
            ],
            'threshold': {
                'line': {'color': "green", 'width': 4},
                'thickness': 0.75,
                'value': memory_savings
            }
        }
    ))

    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )

    return fig


def create_suggestions_table(suggestions: Dict[str, Any]) -> pd.DataFrame:
    """Create detailed table of all preprocessing suggestions."""
    table_data = []

    for category, data in suggestions.items():
        if isinstance(data, dict) and 'suggestions' in data:
            category_name = category.replace('_', ' ').title()
            if category_name not in ['Priorities', 'Summary']:
                priority = data.get('priority', 0)
                suggestion_list = data['suggestions']

                # Priority level
                if priority >= 70:
                    priority_level = '🚨 Critical'
                elif priority >= 50:
                    priority_level = '⚠️ High'
                elif priority >= 30:
                    priority_level = '📝 Medium'
                else:
                    priority_level = '💡 Low'

                # Count issues
                actual_issues = len([s for s in suggestion_list if not s.startswith(
                    '✅') and not s.startswith('ℹ️')])

                # Join suggestions
                suggestions_text = '\n'.join(suggestion_list)

                table_data.append({
                    'Category': category_name,
                    'Priority': f"{priority:.0f}",
                    'Level': priority_level,
                    'Issues': actual_issues,
                    'Suggestions': suggestions_text
                })

    df = pd.DataFrame(table_data)

    # Sort by priority
    if not df.empty:
        df['Priority_Numeric'] = df['Priority'].astype(float)
        df = df.sort_values('Priority_Numeric', ascending=False)
        df = df.drop('Priority_Numeric', axis=1)

    return df


def format_code_snippet(code: str) -> str:
    """Format code snippet for display in Streamlit."""
    # Clean up the code
    lines = code.split('\n')
    cleaned_lines = []

    for line in lines:
        # Remove excessive blank lines
        if line.strip() or (cleaned_lines and cleaned_lines[-1].strip()):
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def create_recommendations_summary(suggestions: Dict[str, Any]) -> str:
    """Create formatted summary of recommendations."""
    summary = suggestions.get('summary', {})

    if not summary:
        return "📊 Analysis complete - see detailed suggestions below."

    urgency = summary.get('urgency', 'Unknown')
    total_issues = summary.get('total_issues', 0)
    high_priority_count = summary.get('high_priority_count', 0)

    summary_text = f"""
## 📋 Preprocessing Summary

**Urgency Level**: {urgency}  
**Total Categories with Issues**: {total_issues}  
**High Priority Items**: {high_priority_count}

{summary.get('text', '')}

### 🎯 Top Recommendations:
"""

    if high_priority_count > 0:
        high_priority_areas = summary.get('high_priority_areas', [])
        for i, area in enumerate(high_priority_areas[:3], 1):  # Top 3
            summary_text += f"{i}. **{area}** - Review and address immediately\n"
    else:
        summary_text += "✅ No critical issues detected - your data is in good shape!\n"

    return summary_text
