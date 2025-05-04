import asyncio
import time
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright_stealth import stealth_async
from urllib.parse import unquote
import random

# Assuming your celery app is configured in 'src.celery_app'
from src.celery_app import celery_app

# --- Configuration (Move to .env or settings file later) ---
BROWSER_LAUNCH_ARGS = [
    '--no-sandbox', # Often needed in Docker/Linux
    '--disable-dev-shm-usage',
    '--disable-gpu',
]
NETWORK_TIMEOUT_SECONDS = 30 # Max time to wait for m3u8 request
PAGE_LOAD_TIMEOUT_SECONDS = 60 # Max time for page navigation

# -----------------------------------------------------------

async def extract_m3u8_from_player_url(player_url: str) -> str | None:
    """
    Uses Playwright to navigate to the player URL and intercept the M3U8 request.
    """
    print(f"Extractor Task: Starting Playwright for {player_url}")
    m3u8_url_result = None
    m3u8_found_event = asyncio.Event() # Event to signal when M3U8 is found

    async def handle_request(request):
        nonlocal m3u8_url_result
        # Check if already found to avoid processing more requests
        if m3u8_found_event.is_set():
             return

        url_lower = request.url.lower()
        # --- More specific M3U8 check ---
        # Look for .m3u8 typically before query params '?'
        if ".m3u8" in url_lower.split('?')[0]:
            print(f"Extractor Task: Intercepted potential M3U8 request: {request.url}")
            # Perform quick validation if needed (e.g., check if it's fetch/xhr)
            # if request.resource_type in ["fetch", "xhr"]:
            m3u8_url_result = request.url
            m3u8_found_event.set() # Signal that we found it
            print("Extractor Task: M3U8 URL captured, setting event.")
            # Optional: Abort further non-essential requests? (Advanced)
            # try:
            #     if not m3u8_found_event.is_set(): # Avoid aborting if we just found it
            #         await request.abort()
            # except Exception:
            #     pass # Ignore errors during abort

    async with async_playwright() as p:
        browser = None
        try:
            print("Extractor Task: Launching browser...")
            browser = await p.chromium.launch(
                headless=True, # Run headless on server
                args=BROWSER_LAUNCH_ARGS
            )
            context = await browser.new_context(
                # Add proxy here if needed for the *second* step
                # proxy={ "server": "http://your-proxy..." },
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', # Example UA
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()
            await page.set_default_timeout(PAGE_LOAD_TIMEOUT_SECONDS * 1000) # Page actions timeout
            await page.set_default_navigation_timeout(PAGE_LOAD_TIMEOUT_SECONDS * 1000) # Navigation timeout

            print("Extractor Task: Applying stealth...")
            await stealth_async(page)

            print("Extractor Task: Setting up network interception...")
            # Listen to REQUESTS to catch the URL *before* the response potentially fails
            await page.route("**/*", lambda route: route.continue_()) # Ensure all requests proceed
            page.on("request", handle_request)

            print(f"Extractor Task: Navigating to player URL: {player_url}")
            try:
                # Navigate and wait for basic load, JS will use the fragment
                await page.goto(player_url, wait_until="domcontentloaded")
                print("Extractor Task: Navigation complete (domcontentloaded). Waiting for M3U8...")
            except PlaywrightTimeoutError:
                print("Extractor Task: Timeout during initial page navigation.")
                return None
            except Exception as nav_err:
                print(f"Extractor Task: Error during navigation: {nav_err}")
                return None

            # --- Wait for the M3U8 ---
            try:
                # Wait for the event to be set by the handler OR a timeout
                print(f"Extractor Task: Waiting up to {NETWORK_TIMEOUT_SECONDS}s for M3U8 event...")
                await asyncio.wait_for(m3u8_found_event.wait(), timeout=NETWORK_TIMEOUT_SECONDS)
                print(f"Extractor Task: M3U8 event received.")
            except asyncio.TimeoutError:
                print(f"Extractor Task: Timeout after {NETWORK_TIMEOUT_SECONDS}s waiting for M3U8 request.")
                # M3U8 URL might have been set just before timeout, check one last time
                if m3u8_url_result:
                     print("Extractor Task: M3U8 URL was captured just before timeout.")
                else:
                     print("Extractor Task: M3U8 URL was not captured.")
                     # Optional: Take screenshot on failure
                     # await page.screenshot(path=f"debug_m3u8_timeout_{int(time.time())}.png")
                     return None # Failed to find it
            except Exception as wait_err:
                 print(f"Extractor Task: Error while waiting for M3U8 event: {wait_err}")
                 return None

            # --- We have the result (or None) ---
            print(f"Extractor Task: Found M3U8 URL: {m3u8_url_result}")
            return m3u8_url_result

        except PlaywrightTimeoutError as e:
             print(f"Extractor Task: Playwright Timeout Error: {e}")
             return None
        except Exception as e:
            print(f"Extractor Task: General Playwright Error: {type(e).__name__} - {e}")
            # Consider taking screenshot on general error if page exists
            # if 'page' in locals() and page:
            #    await page.screenshot(path=f"debug_m3u8_error_{int(time.time())}.png")
            return None
        finally:
            if browser:
                print("Extractor Task: Closing browser...")
                await browser.close()
            print("Extractor Task: Playwright finished.")


# Define the Celery task
@celery_app.task(name="extract_m3u8_task")
def extract_m3u8_task(player_url: str) -> str | None:
    """Celery task wrapper to run the async Playwright function."""
    print(f"Celery Worker: Received task for {player_url}")
    try:
        # Run the async function synchronously using asyncio.run()
        # This is okay within a Celery worker process
        result = asyncio.run(extract_m3u8_from_player_url(player_url))
        print(f"Celery Worker: Scraping result: {'Found URL' if result else 'Not Found'}")
        # Celery task should return the result so it can be retrieved later if needed
        return result
    except Exception as e:
         print(f"Celery Worker: Error running async extractor: {e}")
         # You might want to return None or re-raise depending on retry logic
         return None