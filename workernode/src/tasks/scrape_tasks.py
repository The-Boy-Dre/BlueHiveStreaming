# src/tasks/scrape_tasks.py
import logging
from src.celery_app import celery_app # Import the Celery app instance
from src.config import settings      # Import configuration
from src.scrapers.media_scraper import scrape_for_m3u8 # Import scraper function
import asyncio # Use asyncio for the async scraper function

logger = logging.getLogger(__name__) # Get celery logger


# Define the Celery task
# - bind=True gives access to 'self' (the task instance) for logging, retries etc.
# - autoretry_for specifies exceptions that trigger automatic retries
# - retry_kwargs configures retry behavior
# - track_started=True helps monitoring
@celery_app.task(
    bind=True,
    autoretry_for=(Exception,), # Retry on ANY exception from the scraper
    retry_kwargs={'max_retries': 2, 'countdown': 30}, # Retry max 2 times, wait 30s between
    track_started=True,
    time_limit=settings.SCRAPER_TIMEOUT_SECONDS, # Hard time limit from config
    soft_time_limit=settings.SCRAPER_TIMEOUT_SECONDS - 10 # Soft limit
)
def process_scrape_request(self, job_data: dict):
    """
    Celery task to handle a single scrape request.
    Receives job_data from the queue (sent by Layer 2).
    Expected job_data format: {'targetUrl': '...', 'mediaId': '...', 'mediaType': '...'}
    """
    target_url = job_data.get('targetUrl')
    media_id = job_data.get('mediaId')
    media_type = job_data.get('mediaType')
    job_id = self.request.id # Get the unique Celery job ID

    log_prefix = f"[Celery Task {job_id}]"

    if not target_url:
        logger.error(f"{log_prefix} Missing targetUrl in job_data: {job_data}")
        # Fail permanently if essential data is missing
        # We could raise Ignore() here if we don't want retries for bad data
        raise ValueError("Job data must include 'targetUrl'.")

    logger.info(f"{log_prefix} Received job for {media_type} '{media_id}' - URL: {target_url}")

    try:
        # --- Proxy Setup (pass config if enabled) ---
        proxy_to_use = settings.PROXY_CONFIG if settings.PROXY_ENABLED else None

        # --- Run the async scraper function ---
        # Celery 5+ supports async task functions natively if needed,
        # but calling an async function from sync task needs asyncio.run
        # If scrape_for_m3u8 was sync, you'd just call it directly.
        logger.info(f"{log_prefix} Calling scraper...")
        # If scrape_for_m3u8 is truly async (uses await internally beyond selenium)
        # m3u8_url = asyncio.run(scrape_for_m3u8(target_url, job_id, proxy_to_use))
        # If scrape_for_m3u8 is effectively sync (despite async def, only uses blocking selenium):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        m3u8_url = loop.run_until_complete(scrape_for_m3u8(target_url, job_id, proxy_to_use))
        loop.close()


        if m3u8_url:
            logger.info(f"{log_prefix} SUCCESS! Found M3U8: {m3u8_url}")
            # --- Load Step ---
            # TODO: Implement logic to save the result
            # Example: Send to database update API, publish to another queue, etc.
            # For now, we just return it in the task result
            return {'status': 'success', 'm3u8_url': m3u8_url, 'media_id': media_id, 'media_type': media_type}
        else:
            # Scraper finished but didn't find the URL (not necessarily an error for retry)
             logger.warning(f"{log_prefix} Scraper finished, M3U8 URL not found for {target_url}.")
             # Consider if this should be treated as failure or just empty result
             # Depending on config, Celery might retry if no ValueError was raised in scraper
             return {'status': 'completed_no_url', 'media_id': media_id, 'media_type': media_type}


    except Exception as exc:
        # Log the exception before Celery retries or marks as failed
        logger.error(f"{log_prefix} Scrape failed for {target_url}. Error: {exc}", exc_info=True)
        # If autoretry is configured, Celery handles raising Retry automatically
        # Otherwise, re-raise the exception to mark the task as failed after retries
        raise exc