# src/scrapers/player_url_finder.py

import asyncio
import time
import random
import os
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Page
from playwright_stealth import stealth_async
from urllib.parse import urlparse # To validate the extracted URL

# Assume settings are handled elsewhere (e.g., imported or passed)
# from src.config import settings # If you have proxy/headless settings here

# --- Configuration Constants (Adjust as needed / Move to settings) ---
BROWSER_LAUNCH_ARGS = [
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--disable-gpu',
    # Potentially add --start-maximized if needed and running non-headless
]
# Timeout for waiting for the iframe element itself after clicking play
INTERACTION_TIMEOUT_S = 30 # Timeout for clicks and waits for elements during interaction phase
# How long to wait specifically for iframe src attribute to appear after element is found
IFRAME_SRC_TIMEOUT_SECONDS = 25
# How long to wait for initial page elements/navigation
PAGE_LOAD_TIMEOUT_SECONDS = 60
# How long to wait for the initial play button click action itself (per selector)
CLICK_TIMEOUT_SECONDS = 20

# --- Play Button Selectors (Adapt based on manual inspection of target site) ---
# !!! CRITICAL: You MUST inspect the target site (e.g., 123movies) manually !!!
# !!! using browser developer tools to find the correct selectors for     !!!
# !!! the *initial* play button/overlay. These are only examples.       !!!
INITIAL_PLAY_SELECTORS = [
    "iframe#iframe-embed", # If the iframe IS the initial clickable element
    "#player-button", # Example specific ID
    ".play-btn > a", # Another common pattern
    ".btn-watch", # Another common pattern
    ".video-js .vjs-big-play-button", # VideoJS specific
    ".jwplayer .jw-icon-playback", # JWPlayer specific
    "button[class*='play'], button[id*='play'], div[class*='play-button']", # Generic buttons/divs
    "div[class*='overlay'][style*='display: block']", # Visible overlays (sometimes clickable)
    "//*[contains(@aria-label, 'Play') or contains(@title, 'Play')]", # Buttons by ARIA/Title (XPath)
    # Add more specific selectors for the target site here, prioritize unique IDs if available
]
# The iframe ID you identified
PLAYER_IFRAME_SELECTOR = "iframe#playit"
# -----------------------------------------------------------

# Helper function for saving screenshots (implementation depends on context)
async def save_debug_screenshot_pw(page: Page | None, filename: str, log_prefix: str):
    """Saves a screenshot if the page object is valid."""
    if page and not page.is_closed():
        try:
            # Ensure the directory exists if saving to a subpath
            # e.g., os.makedirs(os.path.dirname(filename), exist_ok=True)
            await page.screenshot(path=filename, full_page=True)
            print(f"{log_prefix} Saved debug screenshot to {filename}")
        except Exception as screen_err:
            print(f"{log_prefix} Could not save screenshot: {type(screen_err).__name__} - {screen_err}")
    else:
        print(f"{log_prefix} Cannot save screenshot, page object is invalid or closed.")


async def click_initial_play_button(page: Page, log_prefix=""):
    """Attempts to find and click the first play button/overlay using a list of selectors."""
    print(f"{log_prefix} Attempting to click initial play button/overlay...")
    for i, selector in enumerate(INITIAL_PLAY_SELECTORS):
        locator = None
        try:
            print(f"{log_prefix} Trying selector {i+1}/{len(INITIAL_PLAY_SELECTORS)}: '{selector}'")
            if selector.startswith("//") or selector.startswith("(//"): # Basic check for XPath
                 # Use .first because multiple elements might match an XPath/CSS selector
                 locator = page.locator(selector).first
            else: # Assume CSS selector
                 locator = page.locator(selector).first

            # Wait briefly for the element to potentially appear and be clickable
            # Increase timeout slightly per selector check
            await locator.wait_for(state="visible", timeout=7000) # 7 second wait per selector

            print(f"{log_prefix} Element found and visible. Attempting click...")
            # Use a longer timeout specifically for the click action itself
            # Add slight random delay before click to mimic human behaviour
            await asyncio.sleep(random.uniform(0.1, 0.4))
            # Use force=True only as a last resort if clicks fail due to overlays Playwright can't see
            await locator.click(timeout=CLICK_TIMEOUT_SECONDS * 1000, delay=random.uniform(50, 150))
            print(f"{log_prefix} Successfully clicked using selector: '{selector}'")
            return True # Click successful, exit function

        except PlaywrightTimeoutError:
            # Element not found or not visible within the timeout for this selector
            print(f"{log_prefix} Timeout waiting for element with selector: '{selector}'")
            continue # Try the next selector in the list
        except Exception as e:
            # Other errors during find/click (e.g., element detached)
            print(f"{log_prefix} Error interacting with selector '{selector}': {type(e).__name__} - {e}")
            continue # Try the next selector

    # If the loop finishes without returning True, no selector worked
    print(f"{log_prefix} Failed to click initial play button using all provided selectors.")
    return False


async def find_player_url(target_url: str, proxy_config: dict | None = None) -> str | None:
    """
    Navigates to the target aggregator URL, clicks the initial play button,
    and extracts the player URL from the '#playit' iframe src.
    """
    log_prefix = f"[PlayerFinder Job] ({os.getpid()})" # Add Process ID for clarity
    print(f"{log_prefix} Starting player URL find for: {target_url}")
    player_url_result = None
    ublock_path = None # Define outside try block

    # --- Configure uBlock Path (MUST MATCH YOUR FOLDER STRUCTURE) ---
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir)) # Assumes src/scrapers/

        # Prioritize check for the potentially nested path first
        path_option_2 = os.path.join(project_root, 'extensions', 'ublock_origin_unpacked', 'uBlock-Origin')
        path_option_1 = os.path.join(project_root, 'extensions', 'ublock_origin_unpacked')

        if os.path.isdir(path_option_2) and os.path.exists(os.path.join(path_option_2, 'manifest.json')):
            ublock_path = path_option_2
            print(f"{log_prefix} Using uBlock path: {ublock_path}")
        elif os.path.isdir(path_option_1) and os.path.exists(os.path.join(path_option_1, 'manifest.json')):
            ublock_path = path_option_1
            print(f"{log_prefix} Using uBlock path: {ublock_path}")
        else:
            print(f"{log_prefix} WARNING: uBlock Origin directory not found at expected locations. Searched '{path_option_1}' and '{path_option_2}'. Proceeding without ad blocker.")
    except Exception as e:
        print(f"{log_prefix} WARNING: Error configuring uBlock path - {e}")
    # --- End uBlock Path Configuration ---

    async with async_playwright() as p:
        browser = None
        page = None # Define page outside try block for final screenshot
        try:
            browser_args = list(BROWSER_LAUNCH_ARGS) # Copy defaults
            if ublock_path:
                browser_args.append(f'--disable-extensions-except={ublock_path}')
                browser_args.append(f'--load-extension={ublock_path}')
                print(f"{log_prefix} Added uBlock launch arguments.")

            proxy_details = None
            # Ensure proxy_config structure is expected by Playwright
            if proxy_config and isinstance(proxy_config, dict) and 'server' in proxy_config:
                proxy_details = proxy_config
                print(f"{log_prefix} Configuring Playwright proxy: {proxy_details['server']}")
            elif proxy_config:
                 print(f"{log_prefix} WARNING: Proxy config provided but format might be incorrect for Playwright. Expected dict with 'server' key.")


            print(f"{log_prefix} Launching browser...")
            browser = await p.chromium.launch(
                headless=True, # Usually True for backend scraping
                args=browser_args,
                proxy=proxy_details
            )
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                ignore_https_errors=True # Can be useful for some sites
            )
            page = await context.new_page()
            await page.set_default_timeout(PAGE_LOAD_TIMEOUT_SECONDS * 1000) # Apply to actions
            await page.set_default_navigation_timeout(PAGE_LOAD_TIMEOUT_SECONDS * 1000) # Apply to navigations

            print(f"{log_prefix} Applying stealth...")
            await stealth_async(page) # Apply stealth patches

            print(f"{log_prefix} Navigating to target URL: {target_url}")
            try:
                response = await page.goto(target_url, wait_until="domcontentloaded")
                print(f"{log_prefix} Navigation complete (status: {response.status if response else 'N/A'}).")
                if response and not response.ok:
                     print(f"{log_prefix} WARNING: Navigation completed but status code was {response.status}.")
                     # Optionally raise an error or return None if navigation failed critically
                # Add a small random delay after page load allows some initial scripts
                await asyncio.sleep(random.uniform(2, 5))
            except PlaywrightTimeoutError:
                print(f"{log_prefix} Timeout during initial page navigation.")
                await save_debug_screenshot_pw(page, f"debug_nav_timeout_{int(time.time())}.png", log_prefix)
                return None
            except Exception as nav_err:
                print(f"{log_prefix} Error during navigation: {type(nav_err).__name__} - {nav_err}")
                await save_debug_screenshot_pw(page, f"debug_nav_error_{int(time.time())}.png", log_prefix)
                return None

            # --- Step 1: Click the initial play button ---
            click_successful = await click_initial_play_button(page, log_prefix)
            if not click_successful:
                print(f"{log_prefix} Could not click initial play button. Cannot proceed.")
                await save_debug_screenshot_pw(page, f"debug_click_fail_{int(time.time())}.png", log_prefix)
                return None # Failed to start the process

            print(f"{log_prefix} Initial click attempt finished. Waiting for iframe '{PLAYER_IFRAME_SELECTOR}'...")
            # Wait a bit longer after the click attempt for JS to potentially insert/update the iframe
            await asyncio.sleep(random.uniform(3, 6))

            # --- Step 2: Find the iframe and extract src ---
            iframe_locator = page.locator(PLAYER_IFRAME_SELECTOR) # Target specific iframe
            extracted_src = None
            try:
                # First wait for the iframe element itself to exist in the DOM (be attached)
                print(f"{log_prefix} Waiting up to {INTERACTION_TIMEOUT_S}s for iframe element '{PLAYER_IFRAME_SELECTOR}' to be attached...")
                await iframe_locator.wait_for(state="attached", timeout=INTERACTION_TIMEOUT_S * 1000) # Use INTERACTION_TIMEOUT_S here
                print(f"{log_prefix} Player iframe element found in DOM.")

                # Now, specifically wait for the 'src' attribute to be populated with a valid URL
                print(f"{log_prefix} Waiting up to {IFRAME_SRC_TIMEOUT_SECONDS}s for iframe src attribute...")
                start_time = time.monotonic()
                while time.monotonic() - start_time < IFRAME_SRC_TIMEOUT_SECONDS:
                    src_value = await iframe_locator.get_attribute("src")
                    # Check if src exists and looks like a valid HTTP/HTTPS URL
                    if src_value and urlparse(src_value).scheme in ['http', 'https']:
                        print(f"{log_prefix} Found valid iframe src: {src_value}")
                        extracted_src = src_value
                        break # Exit loop once valid src is found
                    await asyncio.sleep(0.5) # Check every half second

                # Check if the loop completed without finding the src
                if not extracted_src:
                     print(f"{log_prefix} Timeout: iframe src attribute did not populate or was invalid within {IFRAME_SRC_TIMEOUT_SECONDS}s.")
                     await save_debug_screenshot_pw(page, f"debug_iframe_src_timeout_{int(time.time())}.png", log_prefix)
                     return None # Return None as failure state

            except PlaywrightTimeoutError:
                # This catches the timeout from the initial iframe_locator.wait_for call
                print(f"{log_prefix} Timeout waiting for iframe '{PLAYER_IFRAME_SELECTOR}' element itself to be attached within {INTERACTION_TIMEOUT_S}s.")
                await save_debug_screenshot_pw(page, f"debug_iframe_find_timeout_{int(time.time())}.png", log_prefix)
                return None
            except Exception as iframe_err:
                 print(f"{log_prefix} Error finding/accessing iframe '{PLAYER_IFRAME_SELECTOR}': {type(iframe_err).__name__} - {iframe_err}")
                 await save_debug_screenshot_pw(page, f"debug_iframe_error_{int(time.time())}.png", log_prefix)
                 return None

            player_url_result = extracted_src # Assign the successfully extracted URL
            print(f"{log_prefix} Successfully extracted player URL: {player_url_result}")
            return player_url_result

        except PlaywrightTimeoutError as e:
             print(f"{log_prefix} Playwright Timeout Error during setup or execution: {e}")
             await save_debug_screenshot_pw(page, f"debug_pw_timeout_{int(time.time())}.png", log_prefix)
             return None
        except Exception as e:
            print(f"{log_prefix} General Playwright Error in finder: {type(e).__name__} - {e}")
            await save_debug_screenshot_pw(page, f"debug_finder_general_error_{int(time.time())}.png", log_prefix)
            return None
        finally:
            if browser:
                print(f"{log_prefix} Closing browser...")
                # Add extra checks for safety before closing context/browser
                try:
                     if context and not context.is_closed(): # Check context before closing page
                         if page and not page.is_closed():
                             await page.close()
                         await context.close()
                     # Check browser after context
                     if browser and browser.is_connected():
                         await browser.close()
                except Exception as close_err:
                     print(f"{log_prefix} Error during browser/context cleanup: {close_err}")
            print(f"{log_prefix} Player URL finder finished.")

# --- Example of how to call it (e.g., from a Celery task or test script) ---
# async def main():
#     # Replace with the actual URL of a movie page on the site you target
#     target = "https://ww19.0123movie.net/movie/alien-romulus-1630857469.html" # Example
#     print(f"Attempting to find player URL for: {target}")
#
#     # Example Proxy Configuration (replace with your actual proxy details if needed)
#     # proxy_details = {
#     #     "server": "http://your-proxy-host:port",
#     #     "username": "your-proxy-username", # Optional
#     #     "password": "your-proxy-password"  # Optional
#     # }
#     proxy_details = None # Set to None if no proxy needed for this step
#
#     player_url = await find_player_url(target, proxy_config=proxy_details)
#
#     if player_url:
#         print(f"\n---> SUCCESS: Found player URL: {player_url}")
#         # Now you would typically pass this URL to the m3u8_extractor task
#         # print("\n---> Next step: Pass this URL to the M3U8 extractor task.")
#         # task = extract_m3u8_task.delay(player_url) # Assuming you have the task defined
#     else:
#         print("\n---> FAILED: Could not find player URL.")

# if __name__ == "__main__":
#      # Make sure you have an event loop running if calling directly
#      # Simple way for testing:
#      asyncio.run(main())
#--------------------------------------------------------------------------