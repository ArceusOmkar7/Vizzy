"""
Color Palette Settings Component

Provides UI for selecting and previewing custom color palettes.
"""

import streamlit as st
from style import get_available_palettes, preview_palette, get_color_palette


def render_color_palette_settings():
    """
    Render the color palette selection interface.

    Returns:
        str: Selected palette name
    """
    with st.expander("🎨 Color Palette Settings", expanded=False):
        st.markdown("**Choose a color palette for your visualizations:**")

        # Get available palettes
        available_palettes = get_available_palettes()

        # Color palette selection
        col1, col2 = st.columns([2, 1])

        with col1:
            selected_palette = st.selectbox(
                "Select Color Palette:",
                available_palettes,
                index=0,
                help="Choose a color scheme that will be applied to all charts"
            )

        with col2:
            show_preview = st.checkbox("Show Preview", value=False)

        # Show palette preview
        if show_preview:
            st.markdown(f"**Preview: {selected_palette}**")
            try:
                fig = preview_palette(selected_palette, n_colors=8)
                st.pyplot(fig)
            except Exception as e:
                st.error(f"Error previewing palette: {str(e)}")

        # Show color codes for advanced users
        if st.checkbox("Show Color Codes", value=False):
            colors = get_color_palette(8, selected_palette)
            st.markdown("**Color Codes:**")

            # Display colors in a grid
            cols = st.columns(4)
            for i, color in enumerate(colors):
                with cols[i % 4]:
                    st.markdown(
                        f'<div style="background-color: {color}; padding: 10px; '
                        f'border-radius: 5px; margin: 2px; text-align: center; '
                        f'color: {"white" if _is_dark_color(color) else "black"}; '
                        f'font-family: monospace; font-size: 12px;">{color}</div>',
                        unsafe_allow_html=True
                    )

        return selected_palette


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


def apply_palette_to_session(palette_name):
    """
    Apply the selected palette to the current session.

    Args:
        palette_name (str): Name of the palette to apply
    """
    if 'color_palette' not in st.session_state:
        st.session_state.color_palette = palette_name

    if st.session_state.color_palette != palette_name:
        st.session_state.color_palette = palette_name
        st.rerun()
