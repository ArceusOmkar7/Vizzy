"""
Global styling configuration for the Data Visualizer app.

Defines consistent themes for Streamlit UI and Matplotlib/Seaborn plots.
"""

import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns


def apply_global_style():
    """
    Apply global styling to the Streamlit app and plotting libraries.

    Sets up consistent color schemes, fonts, and layout preferences
    for both the UI and generated visualizations.
    """
    # Streamlit custom CSS
    st.markdown("""
    <style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stMetric {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 0.375rem;
        padding: 1rem;
    }
    
    .stAlert {
        border-radius: 0.375rem;
    }
    
    /* Custom sidebar styling */
    .css-1d391kg {
        padding-top: 2rem;
    }
    
    /* Header styling */
    h1 {
        color: #2c3e50;
        border-bottom: 3px solid #3498db;
        padding-bottom: 0.5rem;
    }
    
    h2 {
        color: #34495e;
        margin-top: 2rem;
    }
    
    h3 {
        color: #34495e;
    }
    </style>
    """, unsafe_allow_html=True)

    # Configure matplotlib and seaborn defaults
    setup_plot_style()


def setup_plot_style():
    """
    Configure default styling for matplotlib and seaborn plots.

    Sets up a consistent, professional look for all generated charts
    with good contrast and readable fonts.
    """
    # Set seaborn style and palette
    sns.set_style("whitegrid")
    sns.set_palette("husl")

    # Configure matplotlib parameters
    plt.rcParams.update({
        'figure.figsize': (10, 6),
        'figure.dpi': 100,
        'savefig.dpi': 150,
        'font.size': 12,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 11,
        'figure.titlesize': 16,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'axes.edgecolor': '#cccccc',
        'axes.linewidth': 0.8,
        'xtick.color': '#666666',
        'ytick.color': '#666666',
        'text.color': '#333333'
    })


def get_color_palette(n_colors=10):
    """
    Get a consistent color palette for charts.

    Args:
        n_colors (int): Number of colors needed

    Returns:
        list: List of hex color codes
    """
    return sns.color_palette("husl", n_colors=n_colors).as_hex()


def apply_chart_theme(fig, title=None):
    """
    Apply consistent theming to a matplotlib figure.

    Args:
        fig (matplotlib.figure.Figure): The figure to style
        title (str, optional): Title to add to the figure

    Returns:
        matplotlib.figure.Figure: The styled figure
    """
    if title:
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)

    # Adjust layout to prevent clipping
    fig.tight_layout()

    return fig
