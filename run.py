# run.py

import subprocess
import time
import signal
import sys

def run():
    try:
        # Start Celery
        celery_proc = subprocess.Popen(
            ["celery", "-A", "celery_worker", "worker", "--loglevel=info"]
        )

        # Give Celery time to spin up
        time.sleep(2)

        # Start Streamlit (blocking)
        streamlit_proc = subprocess.Popen(
            ["streamlit", "run", "streamlit_app/app.py"]
        )

        # Wait for Streamlit to finish
        streamlit_proc.wait()

    except KeyboardInterrupt:
        print("\nShutting down due to KeyboardInterrupt...")

    finally:
        print("Terminating subprocesses...")
        if 'celery_proc' in locals():
            celery_proc.terminate()
        if 'streamlit_proc' in locals() and streamlit_proc.poll() is None:
            streamlit_proc.terminate()

        # Optional: wait for clean shutdown
        time.sleep(1)

if __name__ == "__main__":
    run()
