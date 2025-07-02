"""
Global styling configuration for the Data Visualizer app.

Defines consistent themes for Streamlit UI and Matplotlib/Seaborn plots.
Includes custom color palette selection functionality.
"""

import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns


# Define available color palettes
COLOR_PALETTES = {
    "Default (Husl)": "husl",
    "Professional": ["#2E86AB", "#A23B72", "#F18F01", "#C73E1D", "#4B9F44", "#7B2D8E", "#E85D04", "#023047"],
    "Vibrant": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FFEAA7", "#DDA0DD", "#98D8C8", "#F7DC6F"],
    "Earth Tones": ["#8D5524", "#C68642", "#E0AC69", "#F1C27D", "#FFDBAC", "#A0522D", "#CD853F", "#DEB887"],
    "Ocean": ["#003f5c", "#2f4b7c", "#665191", "#a05195", "#d45087", "#f95d6a", "#ff7c43", "#ffa600"],
    "Sunset": ["#FF9A8B", "#FDBB2D", "#EE1A78", "#833AB4", "#C471ED", "#12C2E9", "#FDA085", "#F093FB"],
    "Monochrome": ["#2C3E50", "#34495E", "#7F8C8D", "#95A5A6", "#BDC3C7", "#D5DBDB", "#ECF0F1", "#F8F9FA"],
    "Pastel": ["#FFB3BA", "#FFDFBA", "#FFFFBA", "#BAFFC9", "#BAE1FF", "#E1BAFF", "#FFBAE1", "#C9FFBA"],
    "Dark": ["#8E44AD", "#E74C3C", "#F39C12", "#27AE60", "#3498DB", "#E67E22", "#16A085", "#9B59B6"],
    "Seaborn Deep": "deep",
    "Seaborn Pastel": "pastel",
    "Seaborn Dark": "dark",
    "Seaborn Colorblind": "colorblind"
}


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


def get_color_palette(n_colors=10, palette_name="Default (Husl)"):
    """
    Get a consistent color palette for charts.

    Args:
        n_colors (int): Number of colors needed
        palette_name (str): Name of the color palette to use

    Returns:
        list: List of hex color codes
    """
    if palette_name not in COLOR_PALETTES:
        palette_name = "Default (Husl)"

    palette = COLOR_PALETTES[palette_name]

    # Handle custom color lists
    if isinstance(palette, list):
        if len(palette) >= n_colors:
            return palette[:n_colors]
        else:
            # Repeat the palette if we need more colors
            repeated = (palette * ((n_colors // len(palette)) + 1))[:n_colors]
            return repeated

    # Handle seaborn palette names
    try:
        return sns.color_palette(palette, n_colors=n_colors).as_hex()
    except:
        # Fallback to default
        return sns.color_palette("husl", n_colors=n_colors).as_hex()


def get_available_palettes():
    """
    Get list of available color palette names.

    Returns:
        list: List of palette names
    """
    return list(COLOR_PALETTES.keys())


def preview_palette(palette_name, n_colors=8):
    """
    Generate a preview of a color palette.

    Args:
        palette_name (str): Name of the palette to preview
        n_colors (int): Number of colors to show

    Returns:
        matplotlib.figure.Figure: Figure showing the color palette
    """
    colors = get_color_palette(n_colors, palette_name)

    fig, ax = plt.subplots(figsize=(10, 2))

    # Create color swatches
    for i, color in enumerate(colors):
        ax.add_patch(plt.Rectangle((i, 0), 1, 1, facecolor=color,
                     edgecolor='white', linewidth=2))
        ax.text(i + 0.5, 0.5, f'{i+1}', ha='center', va='center',
                color='white' if _is_dark_color(color) else 'black', fontweight='bold')

    ax.set_xlim(0, len(colors))
    ax.set_ylim(0, 1)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(f'Color Palette: {palette_name}',
                 fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    return fig


def _is_dark_color(hex_color):
    """
    Determine if a color is dark based on its luminance.

    Args:
        hex_color (str): Hex color code

    Returns:
        bool: True if the color is dark
    """
    # Remove # if present
    hex_color = hex_color.lstrip('#')

    # Convert to RGB
    r = int(hex_color[0:2], 16) / 255.0
    g = int(hex_color[2:4], 16) / 255.0
    b = int(hex_color[4:6], 16) / 255.0

    # Calculate luminance
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return luminance < 0.5


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
