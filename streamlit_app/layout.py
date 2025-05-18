# streamlit_app/layout.py
# Defines the layout components of the Streamlit application,
# including the sidebar and the main content area with split panels.

import streamlit as st
from streamlit_app.form import flight_search_form
from streamlit_app.poll import poll_results
from streamlit_app.display import render_results_table, render_hold_summary

def build_layout():
    """
    Constructs the main UI layout of the application.
    This includes a sidebar for the flight search form and a main area
    for displaying search results and hold details.
    """
    # Sidebar for flight search form
    with st.sidebar:
        st.header("✈️ Flight Search") # Added a header for the sidebar
        flight_search_form()

    # Main content area
    with st.container():
        # Split the main area into two columns: top for results, bottom for hold details.
        # The problem description implies a top/bottom split, not columns,
        # so we'll use separate containers or manage flow with st.expander or similar.
        # For simplicity, using st.container() for logical grouping.

        # Top section for search/poll results table (60% height - conceptual)
        st.subheader("🔍 Flight Search Results")
        # The poll_results function will handle rendering the table via render_results_table
        poll_results(render_results_table)

        st.markdown("---") # Visual separator

        # Bottom section for hold confirmation details (40% height - conceptual)
        st.subheader("📝 Hold Confirmation Details")
        render_hold_summary()


