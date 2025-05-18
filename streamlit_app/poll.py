# streamlit_app/poll.py
# Handles polling for task results from Celery and triggers rendering
# of the results using a provided render function.

import time
import streamlit as st
from celery.result import AsyncResult
from celery_worker import celery
from streamlit_app.state import get_task_id, set_search_offers, set_hold_details

# Define a polling interval (in seconds)
POLLING_INTERVAL = 2 # Check every 2 seconds

def poll_results(render_fn):
    """
    Polls for the result of an asynchronous Celery task.
    Updates the UI based on the task's status (pending, success, failure).

    Args:
        render_fn (callable): A function to call with the task result when ready.
                              This function is responsible for displaying the data.
    """
    task_id = get_task_id()

    if not task_id:
        st.info("Submit a flight search to view results here.")
        return

    is_exist = False
    while not is_exist:
        try:
            task = AsyncResult(task_id, app=celery) # Get the AsyncResult object for the task

            if task.state == "FAILURE":
                st.error(f"❌ Task failed. Error: {task.traceback}")
            elif task.state == "SUCCESS":
                # Task is complete, render the results
                st.success("🎉 Results are ready!")
                task_output = task.get()
                print("## Task OUTPUT ##", task_output)
                if task_output:
                    set_hold_details(task_output['hold_details'])
                render_fn(task_output['offers']) # Pass the actual result data to the render function
                is_exist = True
            else:
                # Task is still pending
                with st.spinner(f"⏳ Searching for flights... (Task ID: {task_id[:8]}...). Please wait."):
                    # Rerun the script to check again after a delay
                    # Note: st.experimental_rerun() will stop execution of current script and rerun from top.
                    # Consider using time.sleep() and st.empty() for a more controlled refresh,
                    # or rely on Streamlit's natural reactivity if other widgets can trigger reruns.
                    # For long-polling, st.experimental_rerun is a common pattern.
                    time.sleep(POLLING_INTERVAL) # Wait before rerunning
        except Exception as e:
            st.error(f"🚨 An error occurred while polling for results: {e}")
            is_exist = True
