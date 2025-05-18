# run.py
import subprocess
import threading
import time

def run_celery():
    subprocess.Popen(["celery", "-A", "celery_worker", "worker", "--loglevel=info"])

def run_streamlit():
    subprocess.call(["streamlit", "run", "streamlit_app/app.py"])

if __name__ == "__main__":
    # Start Celery in a background thread
    threading.Thread(target=run_celery, daemon=True).start()

    # Slight delay to allow celery to start cleanly
    time.sleep(2)

    # Run Streamlit in the foreground
    run_streamlit()
