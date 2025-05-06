# src/tasks/scrape_tasks.py

import asyncio
from celery.exceptions import Ignore
from celery import Task # Import Task for potential custom base class later if needed

# Import your Celery app instance (adjust path if necessary - assuming celery_app.py is in root)
# If celery_app.py is in src/, use `from src.celery_app import celery_app`
# If celery_app.py is in root, this might require path adjustments or different import style
try:
    from src.celery_app import celery_app
except ImportError:
    # Fallback if script is run relative to src/tasks
    import sys
    import os
    # Add project root to path assuming structure workernode/src/tasks
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    from celery_app import celery_app


# Import the actual scraper functions
from src.scrapers.player_url_finder import find_player_url
# Import the M3U8 extractor task function signature
# (Make sure m3u8_extractor.py also defines its task with @celery_app.task)
from src.tasks.m3u8_extractor import extract_m3u8_task # Import the Celery task object

# --- Define Task for Finding Player URL ---

@celery_app.task(
    name="tasks.find_player_url", # Explicit name is good practice
    bind=True, # Gives access to 'self' for retry logic etc.
    autoretry_for=(Exception,), # Automatically retry on any exception defined below
    retry_kwargs={'max_retries': 2, 'countdown': 10}, # Retry twice, 10s apart
    acks_late=True, # Acknowledge task only after completion/failure
    time_limit=300, # Max time for this task (5 minutes) - includes browser launch etc.
    soft_time_limit=280 # Log warning if task exceeds this time
)
# --- MODIFIED: Added job_id parameter ---
def find_player_url_task(self: Task, target_aggregator_url: str, job_id: str | None = None):
# --- END MODIFIED ---
    """
    Celery task to find the intermediate player URL from an aggregator site.
    On success, it chains the call to the m3u8 extractor task.
    """
    # Use the passed job_id in logs if provided, otherwise use Celery's request ID
    task_display_id = job_id if job_id else self.request.id
    log_prefix = f"TASK [find_player_url - {task_display_id}]" # Define prefix for consistency

    print(f"{log_prefix}: Starting for {target_aggregator_url}")
    player_url = None
    try:
        # Run the async Playwright function using asyncio.run()
        # This is acceptable within a Celery task context
        # TODO: Add proxy config handling if needed for this first step
        # proxy_info = get_proxy_config() # Example function
        # player_url = asyncio.run(find_player_url(target_aggregator_url, proxy_config=proxy_info))
        player_url = asyncio.run(find_player_url(target_aggregator_url))

        if player_url:
            print(f"{log_prefix}: SUCCESS - Found Player URL: {player_url}")
            # --- Chain the next task ---
            print(f"{log_prefix}: Queuing m3u8 extraction for {player_url} (Original Job ID: {job_id})")
            # Pass the player_url AND the original job_id to the next task for tracking
            # Note: Ensure extract_m3u8_task accepts job_id as a parameter too!
            extract_m3u8_task.signature(args=(player_url, job_id)).delay() # Pass job_id along
            # Return the found player URL as this task's result
            return player_url
        else:
            print(f"{log_prefix}: FAILED - Player URL not found.")
            # Don't automatically retry if function completed but found nothing
            # Consider raising Ignore() if this is not an error state you want retried
            # raise Ignore() # Tells Celery not to count as failure for retry purposes
            return None # Or simply return None

    # Specific exceptions you might want to NOT retry on immediately
    # except (SpecificScrapingError, NonRecoverableError) as e:
    #    print(f"{log_prefix}: ERROR - Non-retriable error: {type(e).__name__} - {e}")
    #    raise Ignore() # Example of preventing retry for certain errors
    except Exception as e:
        print(f"{log_prefix}: ERROR - Exception occurred: {type(e).__name__} - {e}")
        # Let autoretry handle retries based on the decorator config
        # The exception will be re-raised implicitly by Celery for retry,
        # or ultimately marked as failed after max_retries.
        # You could explicitly re-raise 'raise' here, but letting Celery handle it is standard.
        # For clarity, you might add 'raise' if you want to be explicit.
        raise # Re-raise the exception for Celery's autoretry mechanism

# --- Make sure your M3U8 extractor task is also defined and accepts job_id ---
# Example structure in src/tasks/m3u8_extractor.py:
#
# from celery_app import celery_app
# from src.scrapers.m3u8_extractor_logic import extract_m3u8_from_player_url # Assuming logic is here
# import asyncio
#
# @celery_app.task(name="tasks.extract_m3u8", bind=True, ...) # Add necessary decorator args
# def extract_m3u8_task(self, player_url: str, job_id: str | None = None): # Accept job_id
#     task_display_id = job_id if job_id else self.request.id
#     log_prefix = f"TASK [extract_m3u8 - {task_display_id}]"
#     print(f"{log_prefix}: Starting M3U8 extraction for {player_url}")
#     try:
#         m3u8_url = asyncio.run(extract_m3u8_from_player_url(player_url)) # Call the async logic
#         if m3u8_url:
#             print(f"{log_prefix}: SUCCESS - Extracted M3U8 URL: {m3u8_url}")
#             # TODO: Store the result, send notification, etc.
#             return m3u8_url
#         else:
#             print(f"{log_prefix}: FAILED - M3U8 URL not found.")
#             return None
#     except Exception as e:
#         print(f"{log_prefix}: ERROR - M3U8 extraction failed: {e}")
#         raise # Allow Celery to handle retries/failure