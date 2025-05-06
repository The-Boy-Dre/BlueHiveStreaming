# src/scrapers/player_url_finder.py

import asyncio
import time
import random
import os
from src.config import settings
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Page, Browser, BrowserContext, Error as PlaywrightError
from playwright_stealth import stealth_async
from urllib.parse import urlparse, urlsplit
import traceback # For printing stack traces in debugging

#These arguments are not specific to Playwright or Selenium themselves. They are command-line switches that can be passed directly to the 
# underlying Chrome or Chromium browser executable when it's launched.
if not settings.SCRAPER_HEADLESS:
    print("[Config] Setting launch args for HEADFUL mode.")
    BROWSER_LAUNCH_ARGS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--start-maximized',
        '--disable-infobars',    # Hide "Chrome is being controlled..." bar
        '--disable-popup-blocking',  # Allow script to handle popups more easily
        '--disable-blink-features=AutomationControlled',  # A direct attempt to hide automation. It targets a specific feature in Chrome's Blink rendering engine that sets the navigator.webdriver property in JavaScript to true when automated. Websites frequently check this property to detect bots.
    ]
else:
    print("[Config] Setting launch args for HEADLESS mode.")
    BROWSER_LAUNCH_ARGS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-blink-features=AutomationControlled',
    ]

# Timeout constants
INTERACTION_TIMEOUT_SECONDS = 30 # Timeout for clicks and waits for elements during interaction phase
IFRAME_SRC_TIMEOUT_SECONDS = 25 # How long to wait specifically for iframe src attribute to appear after element is found
PAGE_LOAD_TIMEOUT_SECONDS = settings.SCRAPER_TIMEOUT_SECONDS if hasattr(settings, 'SCRAPER_TIMEOUT_SECONDS') else 60  # How long to wait for initial page elements/navigation
CLICK_TIMEOUT_SECONDS = 20  # How long to wait for the initial play button click action itself (per selector)

#? Site-specific selectors
SITE_SELECTORS = {
    "ww19.0123movie.net": {
        "initial_play": ["a#play-now"],
        "player_iframe": "iframe#playit"
    },
}


async def click_initial_play_button(page: Page, selectors_to_try: list[str], click_timeout_ms: int, log_prefix=""):
    """Attempts to find and click the first play button/overlay using a list of selectors."""
    print(f"{log_prefix} Attempting to click initial play button/overlay using {len(selectors_to_try)} specific selectors...")
    for i, selector in enumerate(selectors_to_try):
        locator = None
        
        try:
            print(f"{log_prefix} Trying selector {i+1}/{len(selectors_to_try)}: '{selector}'")
            if selector.startswith("//") or selector.startswith("(//"):  # Basic check for XPath
                locator = page.locator(selector).first  # Use .first because multiple elements might match an XPath/CSS selector
            else:
                locator = page.locator(selector).first

            print(f"{log_prefix} DEBUG: Before wait_for visible: {selector}")
             # Wait briefly for the element to potentially appear and be clickable
            # Increase timeout slightly per selector check
            await locator.wait_for(state="visible", timeout=7000)
            print(f"{log_prefix} DEBUG: After wait_for visible: {selector}")

            print(f"{log_prefix} Element found and visible. Attempting click...")
             # Use a longer timeout specifically for the click action itself
            # Add slight random delay before click to mimic human behaviour
            await asyncio.sleep(random.uniform(0.1, 0.4))

            print(f"{log_prefix} DEBUG: Before click: {selector}")
            # Use force=True only as a last resort if clicks fail due to overlays Playwright can't see
            await locator.click(timeout=click_timeout_ms, delay=random.uniform(50, 150))
            print(f"{log_prefix} DEBUG: After click: {selector}")

            print(f"{log_prefix} Successfully clicked using selector: '{selector}'")
            return True

        except Exception as inner_e:
            print(f"{log_prefix} DEBUG: Failed for selector '{selector}': {type(inner_e).__name__} - {inner_e}")
            if isinstance(inner_e, PlaywrightTimeoutError):
                print(f"{log_prefix} Timeout for selector: '{selector}'")
            elif isinstance(inner_e, TypeError):
                traceback.print_exc()
            continue # Continue to next selector

    # If the loop finishes without returning True, no selector worked
    print(f"{log_prefix} Failed to click initial play button using all provided selectors.")
    return False


async def find_player_url(target_url: str) -> str | None:
    """
    Navigates to the target aggregator URL, clicks the initial play button,
    and extracts the player URL from the iframe src.
    Uses configuration from src.config.settings.
    """
    log_prefix = f"[PlayerFinder Job] ({os.getpid()})"  # Add Process ID for clarity
    print(f"{log_prefix} Starting player URL find for: {target_url}")
    player_url_result: str | None = None  # Type hint for clarity
    ublock_path: str | None = None  # Define outside try block
    browser: Browser | None = None
    context: BrowserContext | None = None
    page: Page | None = None
    
    # Determine Site Selectors
    parsed_url = urlparse(target_url)
    domain = parsed_url.netloc.replace('www.', '')
    
    # Make sure we have a valid site_config before proceeding
    site_config = SITE_SELECTORS.get(domain)
    if not site_config:
        print(f"{log_prefix} ERROR: No selectors found for domain '{domain}'. Cannot proceed.")
        return None
        
    initial_play_selectors = site_config.get('initial_play', [])
    player_iframe_selector = site_config.get('player_iframe')

    if not initial_play_selectors or not player_iframe_selector:
        print(f"{log_prefix} ERROR: Missing 'initial_play' or 'player_iframe' selectors for domain '{domain}'. Cannot proceed.")
        return None
    print(f"{log_prefix} Using selectors for domain: {domain}")


    # --- Configure uBlock Path (MUST MATCH YOUR FOLDER STRUCTURE) ---------------------------------------------------------------
    try:
        # Assumes this script (player_url_finder.py) is in src/scrapers/
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        adBlocker = os.path.join(project_root, 'extensions', 'ublock_origin_unpacked', 'uBlock-Origin')
        
        if os.path.isdir(adBlocker) and os.path.exists(os.path.join(adBlocker, 'manifest.json')):
            ublock_path = adBlocker
            print(f"{log_prefix} Using uBlock path: {ublock_path}")
        else:
            print(f"{log_prefix} WARNING: uBlock Origin directory not found at expected locations. Searched '{adBlocker}', Proceeding without ad blocker.")
    except Exception as e:
        print(f"{log_prefix} WARNING: Error configuring uBlock path - {e}")
    # --- End uBlock Path Configuration ------------------------------------------------------------------------------------------

   
   
    async with async_playwright() as p:
        try:
            # Prepare Launch Options
            browser_args = list(BROWSER_LAUNCH_ARGS)
            if ublock_path:
                browser_args.extend([
                    f'--disable-extensions-except={ublock_path}',
                    f'--load-extension={ublock_path}',
                ])
                print(f"{log_prefix} Added uBlock launch arguments.")

            # Configure proxy properly
            proxy_details_pw = None
            if settings.PROXY_ENABLED and settings.PROXY_CONFIG:
                proxy_url = settings.PROXY_CONFIG.get('proxy', {}).get('https')
                if proxy_url:
                    # Parse the proxy URL to extract components
                    parsed_proxy = urlsplit(proxy_url)
                    
                    # Check if there are credentials in the URL
                    if parsed_proxy.username and parsed_proxy.password:
                        # Format: Configure server WITHOUT credentials in the URL
                        # and provide username/password separately
                        proxy_details_pw = {
                            "server": f"{parsed_proxy.scheme}://{parsed_proxy.netloc.split('@')[-1]}",
                            "username": parsed_proxy.username,
                            "password": parsed_proxy.password
                        }
                        print(f"{log_prefix} Configuring Playwright proxy with separate authentication.")
                    else:
                        # No credentials in URL
                        proxy_details_pw = {
                            "server": proxy_url
                        }
                    print(f"{log_prefix} Proxy server configured: {proxy_details_pw['server']}")
                else:
                    print(f"{log_prefix} WARNING: Proxy enabled in settings, but couldn't extract valid proxy URL from PROXY_CONFIG.")
            elif settings.PROXY_ENABLED:
                print(f"{log_prefix} WARNING: Proxy enabled in settings, but PROXY_CONFIG dictionary is missing or None.")




            #! --- Launch Browser --------------------------------------------------------------------------------------------------------------
            print(f"{log_prefix} Launching browser (Headless: {settings.SCRAPER_HEADLESS})...")
            browser = await p.chromium.launch(
                headless=os.getenv("HEADLESS_MODE", "true").lower() == "true",  # Use settings value
                args=browser_args,
                proxy=proxy_details_pw, # Pass prepared proxy dict
            )
            print(f"{log_prefix} DEBUG: Browser object type: {type(browser)}, Connected: {browser.is_connected() if browser else 'N/A'}")
            if not browser or not browser.is_connected():
                raise Exception("Browser launch failed or disconnected immediately.")
                
            print(f"{log_prefix} Browser launched.")
            #! --- End Launch Browser --------------------------------------------------------------------------------------------------------



            # Create Context & Page
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York',
                ignore_https_errors=True  # Can be useful for some sites
            )
            
            print(f"{log_prefix} DEBUG: Context object type: {type(context)}")
            if not context:
                raise Exception("Failed to create browser context (returned None).")
            
            page = await context.new_page()
            print(f"{log_prefix} DEBUG: Page object type: {type(page)}")
            if not page:
                print(f"{log_prefix} ERROR: context.new_page() returned None!")
                raise Exception("context.new_page() failed to return a Page object.")

            page_timeout_ms = PAGE_LOAD_TIMEOUT_SECONDS * 1000
            print(f"{log_prefix} DEBUG: Attempting to set default timeout on page object...")
            page.set_default_timeout(page_timeout_ms)
            print(f"{log_prefix} DEBUG: Set default timeout.")
            page.set_default_navigation_timeout(page_timeout_ms)
            print(f"{log_prefix} Context and page created.")

            # Apply stealth
            print(f"{log_prefix} Applying stealth...")
            await stealth_async(page)
            print(f"{log_prefix} Stealth applied.")

            # Navigate with better error handling
            print(f"{log_prefix} Navigating to target URL: {target_url}")
            try:
                response = await page.goto(target_url, wait_until="domcontentloaded")
                if response:
                    print(f"{log_prefix} Navigation complete (status: {response.status}).")
                    if not response.ok:
                        print(f"{log_prefix} WARNING: Navigation status code was {response.status}.")
                else:
                    print(f"{log_prefix} Navigation completed but no response object returned.")
            except PlaywrightError as nav_error:
                print(f"{log_prefix} Navigation error: {nav_error}")
                if "net::ERR_INVALID_AUTH_CREDENTIALS" in str(nav_error):
                    print(f"{log_prefix} ERROR: Proxy authentication failed. Check your proxy credentials.")
                    raise Exception("Proxy authentication failed")
                raise
                
            await asyncio.sleep(random.uniform(2, 5))

            # Step 1: Click the initial play button
            click_successful = await click_initial_play_button(page, initial_play_selectors, CLICK_TIMEOUT_SECONDS * 1000, log_prefix=log_prefix)
            if not click_successful:
                print(f"{log_prefix} Could not click initial play button. Cannot proceed.")
                raise Exception("Failed to click initial play button.")

            print(f"{log_prefix} Initial click attempt finished. Waiting for iframe...")
            await asyncio.sleep(random.uniform(3, 6))



            # Step 2: Find the iframe and extract src
            print(f"{log_prefix} Locating iframe: {player_iframe_selector}")
            iframe_locator = page.locator(player_iframe_selector).first

            print(f"{log_prefix} Waiting up to {INTERACTION_TIMEOUT_SECONDS}s for iframe element to be attached...")
            await iframe_locator.wait_for(state="attached", timeout=INTERACTION_TIMEOUT_SECONDS * 1000)
            print(f"{log_prefix} Player iframe element found in DOM.")

            print(f"{log_prefix} Polling up to {IFRAME_SRC_TIMEOUT_SECONDS}s for valid iframe src attribute...")
            start_time = time.monotonic()
            extracted_src = None
            while time.monotonic() - start_time < IFRAME_SRC_TIMEOUT_SECONDS:
                # --- await the get_attribute call ---
                src_value = await iframe_locator.get_attribute("src")
                # Check if src exists and looks like a valid HTTP/HTTPS URL
                if src_value and urlparse(src_value).scheme in ['http', 'https']:
                    print(f"{log_prefix} Found valid iframe src: {src_value}")
                    extracted_src = src_value
                    break # Exit loop once valid src is found
                await asyncio.sleep(0.5) # Check every half second
                
            # Check if the loop completed without finding the src
            if not extracted_src:
                print(f"{log_prefix} Timeout waiting for valid iframe src attribute within {IFRAME_SRC_TIMEOUT_SECONDS}s.")
                raise Exception("Timeout waiting for iframe src attribute.")

            player_url_result = extracted_src
            print(f"{log_prefix} Successfully extracted player URL: {player_url_result}")

        # --- Main Exception Handling ---
        # Catch specific Playwright errors first if needed
        except PlaywrightTimeoutError as e:
            print(f"{log_prefix} Playwright Timeout Error: {e}")
            player_url_result = None # Ensure result is None on failure
             # Exception is implicitly caught, flow goes to finally
        except PlaywrightError as e:  # Catch other Playwright-specific errors
            print(f"{log_prefix} Playwright Error: {type(e).__name__} - {e}")
            player_url_result = None  # Ensure result is None on failure
            # Exception is implicitly caught, flow goes to finally
        except Exception as e:
            # Catch any other general errors (like potential TypeError or Exceptions raised manually)
            print(f"{log_prefix} General Error in finder: {type(e).__name__} - {e}")
            if isinstance(e, TypeError): traceback.print_exc() # Print stack trace for TypeError
            player_url_result = None  # Ensure result is None on failure
            # Exception is implicitly caught, flow goes to finally
        # --- End Main Exception Handling ---


        finally:
            print(f"{log_prefix} Entering cleanup block...")
            # Playwright handles closing related contexts/pages when browser is closed
            # We only need to ensure browser.close() is called if browser was launched
            if browser:
                try:
                    # Check connection state synchronously before trying async close
                    if browser.is_connected():
                        print(f"{log_prefix} Attempting to close browser...")
                        await browser.close()  # browser.close() is async and handles contexts/pages
                        print(f"{log_prefix} Browser closed.")
                    else:
                        print(f"{log_prefix} Browser already disconnected.")
                except Exception as browser_close_err:
                    print(f"{log_prefix} Error closing browser: {browser_close_err}")
            else:
                # Browser likely failed during launch if it's None here
                print(f"{log_prefix} Browser object was not initialized or launch failed.")

            print(f"{log_prefix} Player URL finder finished.")
            
        # Return the final result (None if any exception occurred)
        return player_url_result