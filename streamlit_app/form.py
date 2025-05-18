# streamlit_app/form.py
# Contains the Streamlit form for collecting flight search input
# and initiating the search and hold task.

import streamlit as st
from streamlit_app.state import set_task_id # get_session is not used directly here
# Assuming core.models and worker.tasks are in paths accessible by Python
# e.g., they are installed or in PYTHONPATH
from core.models import FlightSearchRequest # Placeholder, ensure this path is correct
from worker.tasks import search_and_hold_flight # Placeholder, ensure this path is correct

def flight_search_form():
    """
    Creates and manages the flight search form using Streamlit.
    Collects user input for flight search parameters and submits a task
    to the Celery worker upon submission.
    """
    with st.form("flight_form"):
        st.markdown("##### Enter Flight Details") # Subheading for the form

        # Input fields for flight search
        from_loc = st.text_input("From (Airport Code)", max_chars=3, help="E.g., JFK, LAX")
        to_loc = st.text_input("To (Airport Code)", max_chars=3, help="E.g., LHR, CDG")
        date = st.date_input("Departure Date")
        pax = st.number_input("Passengers", min_value=1, max_value=9, value=1, step=1)
        seat_class_options = ["ECONOMY", "PREMIUM_ECONOMY", "BUSINESS", "FIRST"]
        seat_class = st.selectbox("Class", seat_class_options)

        # Submit button for the form
        submitted = st.form_submit_button("Search Flights")

        if submitted:
            # Validate inputs (basic example)
            if not from_loc or not to_loc:
                st.error("Please enter both 'From' and 'To' locations.")
                return
            if len(from_loc) != 3 or len(to_loc) != 3:
                st.warning("Airport codes should typically be 3 characters long.")

            # Create a flight search request object
            req = FlightSearchRequest(
                from_location=from_loc.upper(),
                to_location=to_loc.upper(),
                departure_date=date.isoformat(), # Convert date to ISO format string
                num_passengers=pax,
                seat_class=seat_class
            )

            try:
                # Asynchronously call the Celery task
                # .model_dump() is a Pydantic method, ensure FlightSearchRequest is a Pydantic model
                task = search_and_hold_flight.delay(req.model_dump())
                set_task_id(task.id) # Store the task ID in session state
                st.success(f"✅ Flight search submitted! Task ID: {task.id}")
                st.info("Results will appear below once processing is complete.")
            except Exception as e:
                st.error(f"❌ Failed to submit task: {e}")
