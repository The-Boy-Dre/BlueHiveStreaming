

import uuid
import os
import sys
from dotenv import load_dotenv

# Load environment variables if needed (e.g., for Celery config)
load_dotenv()

# --- Add src to Python path ---
# This allows importing from 'src' and 'celery_app' directly from the root
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
# Check if the 'src' path is already in the list of paths Python searches for modules
if src_path not in sys.path:
    sys.path.insert(0, src_path)
# --- End Add src path ---


# Import the specific task function we want to trigger
# Make sure the task is defined in the imported file (e.g., scrape_tasks.py)
try:
    # Assuming the task is defined in src/tasks/scrape_tasks.py
    from tasks.scrape_tasks import find_player_url_task
except ImportError:
    print("ERROR: Could not import 'find_player_url_task'.")
    print("Ensure it is defined and decorated with @celery_app.task in src/tasks/scrape_tasks.py")
    print(f"Current Python path includes: {sys.path}")
    exit(1)


# --- Configuration ---
# Hardcoded URL for testing the initial player URL finding step
TARGET_URL = "https://ww19.0123movie.net/movie/alien-romulus-1630857469.html"
# -------------------

def send_job():
    """Sends the initial scraping task to the Celery queue."""

    job_id = f"test_finder_{uuid.uuid4()}" # Unique ID for this test run
    print("-" * 30)
    print(f"Sending job to find player URL:")
    print(f"  Job ID (for logs): {job_id}")
    print(f"  Target URL: {TARGET_URL}")
    print("-" * 30)

    try:
        # Call the .delay() method of the task function
        # Pass the target URL as an argument
        # The task definition includes the logic to run the scraper
        async_result = find_player_url_task.delay(
            target_aggregator_url=TARGET_URL,  
            job_id=job_id
            
            # Add other arguments if your task expects them (e.g., job_id)
            # job_id=job_id # If your task function accepts it
        )
        print(f"\nSuccessfully sent task to Celery!")
        print(f"Celery Task ID: {async_result.id}")     #! Where does the "id" come from 
        print("Check your Celery worker console output for progress...")
        print("\nIf successful, this task should trigger the 'extract_m3u8_task'.")

    except Exception as e:
        print(f"\nError sending task to Celery: {e}")
        print("Please ensure your Celery worker is running and Redis is accessible.")

# This standard Python construct ensures the code inside only runs when the script is executed directly (e.g., `python send_test_job.py`), not when it's imported as a module into another script.
if __name__ == "__main__": #? translates to "if the script is being run directly by the user"
    send_job()  # Explanation: This makes the script executable. When you run it, it calls send_job().