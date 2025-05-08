# src/tasks/m3u8_extractor.py # Assuming this is the file location based on imports

import asyncio
import time
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Page, Browser, BrowserContext, Request # Added Request type hint
from playwright_stealth import stealth_async
from urllib.parse import unquote
import random
from celery import Task # Import Celery Task type for binding

# Assuming your celery app is configured in 'src.celery_app' or root
# Adjust import as needed
try:
    # If celery_app.py is in root
    from celery_app import celery_app
except ImportError:
    # Fallback if celery_app.py is in src/
    try:
        from src.celery_app import celery_app
    except ImportError:
         print("FATAL: Could not import celery_app. Check location and Python path.")
         # You might want sys.exit(1) here if running directly
         raise

# --- Configuration (Consider moving to settings or passing via task args) ---
# Re-using BROWSER_LAUNCH_ARGS, but maybe m3u8 extractor needs different settings?
BROWSER_LAUNCH_ARGS = [
    '--no-sandbox', # Often needed in Docker/Linux
    '--disable-dev-shm-usage',
    '--disable-gpu', # Usually needed for headless
]
NETWORK_TIMEOUT_SECONDS = 45 # Increased timeout slightly for finding M3U8
PAGE_LOAD_TIMEOUT_SECONDS = 60 # Max time for player page navigation

# -----------------------------------------------------------

# --- Async Playwright Logic ---
async def extract_m3u8_from_player_url(player_url: str, log_prefix: str = "Extractor") -> str | None:
    """
    Uses Playwright to navigate to the player URL and intercept the M3U8 request.
    Accepts a log_prefix for better tracking.
    """
    print(f"[{log_prefix}] Starting Playwright for {player_url}")
    m3u8_url_result: str | None = None
    m3u8_found_event = asyncio.Event() # Event to signal when M3U8 is found

    # --- Network Request Handler ---
    async def handle_request(request: Request): # Added Request type hint
        nonlocal m3u8_url_result
        # Check if already found or if it's not a relevant request type
        if m3u8_found_event.is_set() or request.resource_type not in ["fetch", "xhr", "other"]:
             # Ignore non-data requests or if already found
             return

        url_lower = request.url.lower()
        # Look for .m3u8 typically before query params '?'
        # Added check for common manifest names too
        if ".m3u8" in url_lower.split('?')[0] or "manifest" in url_lower or "playlist" in url_lower:
            print(f"[{log_prefix}] Intercepted potential M3U8/Manifest request: {request.url}")
            # Store the first one found that seems plausible
            if not m3u8_url_result:
                m3u8_url_result = request.url
                m3u8_found_event.set() # Signal that we found it
                print(f"[{log_prefix}] M3U8 URL captured: {m3u8_url_result}, setting event.")
            # Optional: Abort further non-essential requests? (Advanced)
            # Be careful not to abort the m3u8 request itself if route is used differently
    # --- End Network Request Handler ---

    async with async_playwright() as p:
        browser: Browser | None = None
        context: BrowserContext | None = None
        page: Page | None = None
        try:
            print(f"[{log_prefix}] Launching browser...")
            # TODO: Decide if proxy/ublock are needed for this second step.
            # Often they might NOT be needed if the player URL already contains tokens.
            # Pass proxy_details_pw=settings.PROXY_CONFIG... if needed
            # Pass ublock launch args if needed
            browser = await p.chromium.launch(
                headless=True, # Usually run headless on server for this step
                args=BROWSER_LAUNCH_ARGS
            )
            # Debug check after launch
            print(f"[{log_prefix}] DEBUG: Browser object type: {type(browser)}, Connected: {browser.is_connected() if browser else 'N/A'}")
            if not browser or not browser.is_connected(): raise Exception("Browser launch failed or disconnected.")
            print(f"[{log_prefix}] Browser launched.")


            context = await browser.new_context(
                # Proxy / http_credentials should be set here if needed for movuna.xyz etc.
                # proxy={...},
                # http_credentials={...},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                ignore_https_errors=True # Often useful
            )
            print(f"[{log_prefix}] DEBUG: Context object type: {type(context)}")
            if not context: raise Exception("Failed to create browser context.")

            page = await context.new_page()
            print(f"[{log_prefix}] DEBUG: Page object type: {type(page)}")
            if not page: raise Exception("context.new_page() failed.")

            page_timeout_ms = PAGE_LOAD_TIMEOUT_SECONDS * 1000
            page.set_default_timeout(page_timeout_ms) # Synchronous
            page.set_default_navigation_timeout(page_timeout_ms) # Synchronous
            print(f"[{log_prefix}] Context and page created.")

            print(f"[{log_prefix}] Applying stealth...")
            await stealth_async(page) # Apply stealth patches
            print(f"[{log_prefix}] Stealth applied.")

            print(f"[{log_prefix}] Setting up network interception...")
            # Listen to REQUESTS to catch the URL *before* the response potentially fails or is blocked
            # Ensure request interception is enabled if aborting needed (but not needed here)
            # await page.route("**/*", lambda route: route.continue_()) # Only needed if aborting/modifying
            page.on("request", handle_request) # Listen for requests

            print(f"[{log_prefix}] Navigating to player URL: {player_url}")
            try:
                # Navigate and wait for basic load, JS will use the fragment
                # 'load' might be safer here to ensure player scripts run
                response = await page.goto(player_url, wait_until="load", timeout=page_timeout_ms)
                print(f"[{log_prefix}] Navigation complete (status: {response.status if response else 'N/A'}, wait=load). Waiting for M3U8...")
                # Optional: Add a small delay AFTER load for player init scripts
                await asyncio.sleep(random.uniform(2, 4))
            except PlaywrightTimeoutError:
                print(f"[{log_prefix}] Timeout during player page navigation.")
                # Optionally save screenshot
                # await save_debug_screenshot_pw(page, f"debug_m3u8_nav_timeout_{int(time.time())}.png", log_prefix)
                # Don't return here, let finally handle cleanup
                raise # Re-raise to be caught by main handler
            except Exception as nav_err:
                print(f"[{log_prefix}] Error during player page navigation: {nav_err}")
                # await save_debug_screenshot_pw(page, f"debug_m3u8_nav_error_{int(time.time())}.png", log_prefix)
                raise # Re-raise

            # --- Wait for the M3U8 ---
            try:
                # Wait for the event to be set by the handler OR a timeout
                print(f"[{log_prefix}] Waiting up to {NETWORK_TIMEOUT_SECONDS}s for M3U8 request event...")
                await asyncio.wait_for(m3u8_found_event.wait(), timeout=NETWORK_TIMEOUT_SECONDS)
                print(f"[{log_prefix}] M3U8 request event received.")
            except asyncio.TimeoutError:
                print(f"[{log_prefix}] Timeout after {NETWORK_TIMEOUT_SECONDS}s waiting for M3U8 request.")
                # M3U8 URL might have been set just before timeout, check one last time
                if m3u8_url_result:
                     print(f"[{log_prefix}] M3U8 URL was captured just before timeout.")
                else:
                     print(f"[{log_prefix}] M3U8 URL was not captured.")
                     # Optionally save screenshot
                     # await save_debug_screenshot_pw(page, f"debug_m3u8_event_timeout_{int(time.time())}.png", log_prefix)
                     # Raise an exception so the calling task knows it failed
                     raise Exception("Timeout waiting for M3U8 network request.")
            except Exception as wait_err:
                 print(f"[{log_prefix}] Error while waiting for M3U8 event: {wait_err}")
                 raise # Re-raise

            # --- We have the result (or raised exception) ---
            print(f"[{log_prefix}] Found M3U8 URL: {m3u8_url_result}")
            # Return successful result, finally block will run

        except Exception as e:
            # Catch errors from navigation, waiting, or general setup
            print(f"[{log_prefix}] Error during M3U8 extraction process: {type(e).__name__} - {e}")
            # Optionally save screenshot
            # await save_debug_screenshot_pw(page, f"debug_m3u8_main_error_{int(time.time())}.png", log_prefix)
            m3u8_url_result = None # Ensure failure state
            # Let finally block run before returning None implicitly or explicitly
        finally:
            # Ensure browser cleanup happens
            if browser:
                print(f"[{log_prefix}] Closing browser...")
                try:
                     if browser.is_connected(): await browser.close()
                     else: print(f"[{log_prefix}] Browser already disconnected.")
                except Exception as close_err: print(f"[{log_prefix}] Error closing browser: {close_err}")
            else: print(f"[{log_prefix}] Browser object was not initialized.")
            print(f"[{log_prefix}] M3U8 extractor Playwright finished.")

        return m3u8_url_result # Return None if any exception occurred


# --- Define the Celery task ---
@celery_app.task(
    name="tasks.extract_m3u8", # Explicit name matching the import
    bind=True, # Allow access to self.request
    autoretry_for=(Exception,), # Automatically retry on standard Exceptions
    retry_kwargs={'max_retries': 1, 'countdown': 60}, # Example: Retry once after 60s
    acks_late=True, # Acknowledge task only after completion/failure
    time_limit=360, # Allow more time for this step (6 minutes)
    soft_time_limit=330
)
# --- MODIFIED: Added job_id parameter ---
def extract_m3u8_task(self: Task, player_url: str, job_id: str | None = None):
# --- END MODIFIED ---
    """Celery task wrapper to run the async Playwright function to extract M3U8."""
    # Use the tracking ID in logs
    task_display_id = job_id if job_id else self.request.id
    log_prefix = f"TASK [extract_m3u8 - {task_display_id}]" # Consistent log prefix

    print(f"{log_prefix}: Received task for {player_url}")
    m3u8_url_result = None # Initialize result
    try:
        # Run the async function synchronously using asyncio.run()
        # Pass the log_prefix from the task level to the async function
        m3u8_url_result = asyncio.run(extract_m3u8_from_player_url(player_url, log_prefix=log_prefix))

        if m3u8_url_result:
            print(f"{log_prefix}: Scraping result: Found URL -> {m3u8_url_result}")
            # TODO: Add logic here to STORE or use the final m3u8_url
            # e.g., save to database associated with job_id, etc.
        else:
            print(f"{log_prefix}: Scraping result: M3U8 URL Not Found.")
            # Decide if not finding the URL is an error state that should trigger retry
            # For now, we just return None, letting the task succeed with no result.
            # To trigger retry on failure, raise an exception here.
            # raise ValueError("M3U8 URL could not be extracted.")

        # Celery task returns the result (string or None)
        return m3u8_url_result
    except Exception as e:
         print(f"{log_prefix}: ERROR - Running async extractor failed: {type(e).__name__} - {e}")
         # Let Celery's autoretry handle this based on the decorator
         raise # Re-raise the exception for Celery