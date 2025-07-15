"""
State Management Utilities for Vizzy

Provides helper functions for managing Streamlit session state without causing tab switches.
"""

import streamlit as st


def set_state_flag(key: str, value=True):
    """
    Set a temporary flag in session state.

    Args:
        key (str): The session state key
        value: The value to set (default: True)
    """
    st.session_state[key] = value


def get_and_clear_flag(key: str):
    """
    Get a flag value and immediately clear it from session state.

    Args:
        key (str): The session state key

    Returns:
        The flag value if it exists, None otherwise
    """
    if key in st.session_state:
        value = st.session_state[key]
        del st.session_state[key]
        return value
    return None


def show_success_if_flag(flag_key: str, message: str):
    """
    Show a success message if a flag is set, then clear the flag.

    Args:
        flag_key (str): The session state flag key
        message (str): The success message to display
    """
    if get_and_clear_flag(flag_key):
        st.success(message)


def show_info_if_flag(flag_key: str, message: str):
    """
    Show an info message if a flag is set, then clear the flag.

    Args:
        flag_key (str): The session state flag key
        message (str): The info message to display
    """
    if get_and_clear_flag(flag_key):
        st.info(message)


def show_warning_if_flag(flag_key: str, message: str):
    """
    Show a warning message if a flag is set, then clear the flag.

    Args:
        flag_key (str): The session state flag key
        message (str): The warning message to display
    """
    if get_and_clear_flag(flag_key):
        st.warning(message)


def safe_button_click(key: str, callback=None, *args, **kwargs):
    """
    Handle button clicks safely without causing page reloads.

    Args:
        key (str): Unique key for the button state
        callback: Optional callback function to execute
        *args, **kwargs: Arguments to pass to the callback

    Returns:
        True if button was clicked, False otherwise
    """
    button_key = f"button_{key}"

    if button_key in st.session_state and st.session_state[button_key]:
        # Button was clicked, execute callback if provided
        if callback:
            callback(*args, **kwargs)

        # Clear the button state
        st.session_state[button_key] = False
        return True

    return False


def init_session_state(defaults: dict):
    """
    Initialize session state with default values if not already set.

    Args:
        defaults (dict): Dictionary of key-value pairs for session state
    """
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
