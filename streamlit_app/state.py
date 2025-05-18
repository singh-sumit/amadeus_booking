# streamlit_app/state.py
# Helper functions for managing session state in the Streamlit application.
# Used to store and retrieve data like task IDs and hold information across reruns.

import streamlit as st

def init_session():
    """
    Initializes session state variables if they don't already exist.
    This function is typically called at the beginning of the app's execution.
    """
    # Initialize 'task_id' to None if not already set
    if "task_id" not in st.session_state:
        st.session_state["task_id"] = None

    # Initialize 'hold' to an empty dictionary if not already set
    # This will store details about the flight hold.
    st.session_state["hold"] = {}
    st.session_state["offers"] = {}

    # You can initialize other session state variables here as needed
    # For example:
    # if "search_results" not in st.session_state:
    #     st.session_state["search_results"] = None
    # if "user_preferences" not in st.session_state:
    #     st.session_state["user_preferences"] = {}

def set_task_id(task_id: str):
    """
    Sets the 'task_id' in the session state.

    Args:
        task_id (str): The ID of the Celery task.
    """
    st.session_state["task_id"] = task_id

def get_task_id() -> str | None:
    """
    Retrieves the 'task_id' from the session state.

    Returns:
        str or None: The task ID if set, otherwise None.
    """
    return st.session_state.get("task_id")

def set_hold_details(details: dict):
    """
    Sets the 'hold' details in the session state.

    Args:
        details (dict): A dictionary containing flight hold information.
    """
    st.session_state["hold"] = details

def get_hold_details() -> dict:
    """
    Retrieves the 'hold' details from the session state.

    Returns:
        dict: The hold details dictionary.
    """
    return st.session_state.get("hold", {}) # Return empty dict if not found

# Example of how you might store search results if not directly passed to display
def set_search_offers(offers: list):
    st.session_state["offers"] = offers

def get_search_offers() -> list | None:
    return st.session_state.get("offers")

