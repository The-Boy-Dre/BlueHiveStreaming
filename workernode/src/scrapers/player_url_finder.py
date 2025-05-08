# src/scrapers/player_url_finder.py

import asyncio
import time
import random
import os
from src.config import settings # Ensure this imports your settings object correctly
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Page, Browser, BrowserContext, Error as PlaywrightError, Locator
from playwright_stealth import stealth_async
from urllib.parse import urlparse, urlsplit
import traceback # For printing stack traces in debugging

# These arguments are not specific to Playwright or Selenium themselves. They are command-line switches 
# that can be passed directly to the underlying Chrome or Chromium browser executable when it's launched.
if not settings.SCRAPER_HEADLESS:
    print("[Config] Setting launch args for HEADFUL mode.")
    BROWSER_LAUNCH_ARGS = [
        '--no-sandbox',                 # Often needed in containerized/CI environments
        '--disable-dev-shm-usage',      # Overcomes limited resource problems
        '--disable-gpu',                # Often recommended for headless, can help stability
        '--start-maximized',            # Ensures viewport is maximized for headful
        '--disable-infobars',           # Hide "Chrome is being controlled..." bar
        '--disable-popup-blocking',     # Allow script to handle popups more easily if needed
        # A direct attempt to hide automation. It targets a specific feature in Chrome's Blink 
        # rendering engine that sets the navigator.webdriver property in JavaScript to true 
        # when automated. Websites frequently check this property to detect bots.
        '--disable-blink-features=AutomationControlled',  
    ]
else:
    print("[Config] Setting launch args for HEADLESS mode.")
    BROWSER_LAUNCH_ARGS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-blink-features=AutomationControlled', # Still useful in headless
    ]

# Timeout constants (converted to milliseconds for Playwright, with original comments adapted)
# Timeout for clicks and waits for elements during interaction phase
INTERACTION_TIMEOUT_MS = (settings.SCRAPER_INTERACTION_TIMEOUT_SECONDS * 1000
                          if hasattr(settings, 'SCRAPER_INTERACTION_TIMEOUT_SECONDS') else 30 * 1000)
# How long to wait specifically for iframe src attribute to appear after element is found (polling)
IFRAME_SRC_POLL_TIMEOUT_MS = (settings.SCRAPER_IFRAME_POLL_SECONDS * 1000
                              if hasattr(settings, 'SCRAPER_IFRAME_POLL_SECONDS') else 25 * 1000)
# How long to wait for initial page elements/navigation
PAGE_LOAD_TIMEOUT_MS = (settings.SCRAPER_TIMEOUT_SECONDS * 1000
                        if hasattr(settings, 'SCRAPER_TIMEOUT_SECONDS') else 60 * 1000)
# How long to wait for the click action itself (per selector)
CLICK_TIMEOUT_MS = (settings.SCRAPER_CLICK_TIMEOUT_SECONDS * 1000
                    if hasattr(settings, 'SCRAPER_CLICK_TIMEOUT_SECONDS') else 20 * 1000)


#? Site-specific selectors (New structure for multi-hop and action-based processing)
# THIS IS THE DATA STRUCTURE YOU MODIFIED. The Python code below reads this.
SITE_SELECTORS = {
    "ww19.0123movie.net": {
        "actions": [
            {
            "type": "click", 
             "selectors": ["a#play-now"], # Original: "initial_play": ["a#play-now"]
             "post_click_wait_s": (3, 6) }, # Simulates user pause after click
            {
            "type": "extract_iframe_src", 
             "iframe_selector": "iframe#playit"} # Original: "player_iframe": "iframe#playit"
        ],
        "next_expected_domain_hint": "movuna.xyz"
    },
    "movuna.xyz": {
        "actions": [
           { # Action for movuna.xyz: Try to extract iframe src directly
            "type": "extract_iframe_src",
             # "parent_selector": "div#player", # You commented this out, so it looks globally
             "iframe_selector": "iframe[src*='vidsrc.xyz']", # New: More specific iframe targeting
             "iframe_src_poll_timeout_ms": IFRAME_SRC_POLL_TIMEOUT_MS # Can override if needed for this specific site
           }
        ],
        "next_expected_domain_hint": "vidsrc.xyz"
    },
    "vidsrc.xyz": { # This is likely the final player page for m3u8 extraction
        "is_final_player_host": True
        # Actions can be added here if vidsrc.xyz itself needs interaction handled by *this* script
        # before passing the URL to the m3u8_extractor.
    }
    # ... other site configurations
}

async def find_and_click_element(page: Page, selectors_to_try: list[str], click_timeout_ms: int, log_prefix=""):
    """Attempts to find and click an element using a list of selectors."""
    # Original comment from click_initial_play_button:
    # "Attempts to find and click the first play button/overlay using a list of selectors."
    # This function is now more general.
    print(f"{log_prefix} Attempting click using {len(selectors_to_try)} selectors...")
    for i, selector in enumerate(selectors_to_try):
        locator: Locator | None = None # Original: locator = None (kept for clarity although assigned below)
        try:
            print(f"{log_prefix} Trying selector {i+1}/{len(selectors_to_try)}: '{selector}'")
            # Original logic for XPath check implicitly handled by Playwright's robust locator strategy
            # Playwright locators can be CSS or XPath.
            # Original: if selector.startswith("//") or selector.startswith("(//"): # Basic check for XPath
            # locator = page.locator(selector).first
            # else:
            # locator = page.locator(selector).first
            locator = page.locator(selector).first # Use .first because multiple elements might match

            # Original: print(f"{log_prefix} DEBUG: Before wait_for visible: {selector}")
            # Original: # Wait briefly for the element to potentially appear and be clickable
            # Original: # Increase timeout slightly per selector check
            # Using a fixed reasonable timeout for visibility here, main click has its own timeout.
            print(f"{log_prefix} DEBUG: Waiting for visible: '{selector}' (timeout: 7000ms for visibility)")
            await locator.wait_for(state="visible", timeout=7000) 
            # Original: print(f"{log_prefix} DEBUG: After wait_for visible: {selector}")
            print(f"{log_prefix} DEBUG: Element visible: '{selector}'")

            # Original: print(f"{log_prefix} Element found and visible. Attempting click...")
            # Original: # Use a longer timeout specifically for the click action itself
            # Original: # Add slight random delay before click to mimic human behaviour
            await asyncio.sleep(random.uniform(0.1, 0.4)) 

            # Original: print(f"{log_prefix} DEBUG: Before click: {selector}")
            # Original: # Use force=True only as a last resort if clicks fail due to overlays Playwright can't see
            # `force=True` is not used by default, but can be added to locator.click if specific sites require it.
            print(f"{log_prefix} DEBUG: Attempting click: '{selector}' (timeout: {click_timeout_ms}ms)")
            await locator.click(timeout=click_timeout_ms, delay=random.uniform(50, 150)) # click_timeout_ms is passed in
            # Original: print(f"{log_prefix} DEBUG: After click: {selector}")
            print(f"{log_prefix} DEBUG: After click: '{selector}'")

            print(f"{log_prefix} Successfully clicked using selector: '{selector}'")
            return True
        except Exception as inner_e:
            # Original: print(f"{log_prefix} DEBUG: Failed for selector '{selector}': {type(inner_e).__name__} - {inner_e}")
            print(f"{log_prefix} DEBUG: Click failed for selector '{selector}': {type(inner_e).__name__} - {inner_e}")
            if isinstance(inner_e, PlaywrightTimeoutError):
                # Original: print(f"{log_prefix} Timeout for selector: '{selector}'")
                print(f"{log_prefix} Timeout for selector: '{selector}' during wait_for or click.")
            elif isinstance(inner_e, TypeError): # Original: elif isinstance(inner_e, TypeError):
                traceback.print_exc() # Original: traceback.print_exc()
            # Original: continue # Continue to next selector (implicit in loop)
            continue 
            
    # Original: # If the loop finishes without returning True, no selector worked
    # Original: print(f"{log_prefix} Failed to click initial play button using all provided selectors.")
    print(f"{log_prefix} Failed to click using any of the provided selectors.")
    return False


async def find_player_url(initial_target_url: str, max_hops: int = 5) -> str | None:
    """
    Navigates through a series of pages/iframes based on SITE_SELECTORS
    to find the final player URL.
    Uses configuration from src.config.settings.
    """
    log_prefix = f"[PlayerFinder Job] ({os.getpid()})"  # Add Process ID for clarity (Original Comment)
    print(f"{log_prefix} Starting multi-hop player URL find for: {initial_target_url}")

    current_url_to_process = initial_target_url
    final_player_url: str | None = None  # Type hint for clarity (Original Comment)
    
    browser: Browser | None = None
    context: BrowserContext | None = None # Added for completeness, page is main interaction object per hop
    # Page will be created after browser launch and reused across hops.

    # --- Configure uBlock Path (MUST MATCH YOUR FOLDER STRUCTURE) --- (Original Section Comment)
    ublock_path: str | None = None  # Define outside try block (Original Comment)
    try:
        # Assumes this script (player_url_finder.py) is in src/scrapers/ (Original Comment)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir))
        adblocker_extension_path = os.path.join(project_root, 'extensions', 'ublock_origin_unpacked', 'uBlock-Origin')
        
        if os.path.isdir(adblocker_extension_path) and os.path.exists(os.path.join(adblocker_extension_path, 'manifest.json')):
            ublock_path = adblocker_extension_path
            print(f"{log_prefix} Using uBlock path: {ublock_path}")
        else:
            # Original wording adapted:
            print(f"{log_prefix} WARNING: uBlock Origin directory not found at '{adblocker_extension_path}'. Proceeding without ad blocker.")
    except Exception as e:
        print(f"{log_prefix} WARNING: Error configuring uBlock path - {e}")
    # --- End uBlock Path Configuration --- (Original Section Comment)

    async with async_playwright() as p:
        page: Page | None = None # Define page here to ensure it's in scope for finally if browser launches
        try:
            # Prepare Launch Options
            effective_browser_args = list(BROWSER_LAUNCH_ARGS) 
            if ublock_path:
                effective_browser_args.extend([
                    f'--disable-extensions-except={ublock_path}',
                    f'--load-extension={ublock_path}',
                ])
                print(f"{log_prefix} Added uBlock launch arguments.") # Original comment was similar

            # Configure proxy properly (Original section had similar detailed comments)
            proxy_details_pw = None
            if settings.PROXY_ENABLED and settings.PROXY_CONFIG:
                proxy_url_from_config = settings.PROXY_CONFIG.get('proxy', {}).get('https')
                if proxy_url_from_config:
                    # Parse the proxy URL to extract components (Original comment)
                    parsed_proxy = urlsplit(proxy_url_from_config)
                    
                    # Check if there are credentials in the URL (Original comment)
                    if parsed_proxy.username and parsed_proxy.password:
                        # Format: Configure server WITHOUT credentials in the URL
                        # and provide username/password separately (Original comment)
                        proxy_details_pw = {
                            "server": f"{parsed_proxy.scheme}://{parsed_proxy.netloc.split('@')[-1]}",
                            "username": parsed_proxy.username,
                            "password": parsed_proxy.password
                        }
                        print(f"{log_prefix} Configuring Playwright proxy with separate authentication.") # Original comment
                    else:
                        # No credentials in URL (Original comment)
                        proxy_details_pw = {"server": proxy_url_from_config}
                    print(f"{log_prefix} Proxy server configured: {proxy_details_pw['server']}") # Original comment
                else:
                    print(f"{log_prefix} WARNING: Proxy enabled, but couldn't extract valid proxy URL from PROXY_CONFIG.") # Original comment
            elif settings.PROXY_ENABLED:
                print(f"{log_prefix} WARNING: Proxy enabled, but PROXY_CONFIG dictionary is missing or None.") # Original comment


            #! --- Launch Browser -------------------------------------------------------------------------------------------------------------- (Original Marker)
            # Determine actual headless mode based on environment variable
            actual_headless_mode = os.getenv("HEADLESS_MODE", "true").lower() == "true"
            print(f"{log_prefix} Launching browser (Headless: {actual_headless_mode})...") # Log the actual mode being used
            browser = await p.chromium.launch(
                headless=actual_headless_mode, # Use actual headless mode determined by env var
                args=effective_browser_args,
                proxy=proxy_details_pw, # Pass prepared proxy dict
            )
            # Original: print(f"{log_prefix} DEBUG: Browser object type: {type(browser)}, Connected: {browser.is_connected() if browser else 'N/A'}")
            print(f"{log_prefix} DEBUG: Browser object type: {type(browser)}, Connected: {browser.is_connected() if browser else 'N/A (Launch Failed)'}")
            if not browser or not browser.is_connected():
                raise Exception("Browser launch failed or disconnected immediately.")
            print(f"{log_prefix} Browser launched.") # Original comment
            #! --- End Launch Browser -------------------------------------------------------------------------------------------------------- (Original Marker)


            # Create Context & Page (Original section title)
            # Provide defaults if USER_AGENT or VIEWPORT are not in settings, with a warning
            user_agent_to_use = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36' # Default
            if hasattr(settings, 'USER_AGENT') and settings.USER_AGENT: # Check if USER_AGENT is defined and not empty
                user_agent_to_use = settings.USER_AGENT
            else:
                print(f"{log_prefix} WARNING: 'USER_AGENT' not found or empty in settings. Using a default User-Agent. Please define it in src/config/settings.py.")

            viewport_to_use = {'width': 1280, 'height': 720} # Default
            if hasattr(settings, 'VIEWPORT') and settings.VIEWPORT: # Check if VIEWPORT is defined and not empty
                viewport_to_use = settings.VIEWPORT
            else:
                print(f"{log_prefix} WARNING: 'VIEWPORT' not found or empty in settings. Using a default viewport (1280x720). Please define it in src/config/settings.py.")

            context = await browser.new_context(
                user_agent=user_agent_to_use, 
                viewport=viewport_to_use,    
                locale='en-US',                 
                timezone_id='America/New_York', 
                ignore_https_errors=True  # Can be useful for some sites (Original Comment)
            )
            
            # Original: print(f"{log_prefix} DEBUG: Context object type: {type(context)}")
            print(f"{log_prefix} DEBUG: Context object type: {type(context)}")
            if not context: raise Exception("Failed to create browser context (returned None).") # Original comment wording
            
            page = await context.new_page()
            # Original: print(f"{log_prefix} DEBUG: Page object type: {type(page)}")
            print(f"{log_prefix} DEBUG: Page object type: {type(page)}")
            if not page: 
                # Original: print(f"{log_prefix} ERROR: context.new_page() returned None!")
                # Original: raise Exception("context.new_page() failed to return a Page object.")
                raise Exception("context.new_page() failed to return a Page object.")

            # Original: page_timeout_ms = PAGE_LOAD_TIMEOUT_SECONDS * 1000 (now PAGE_LOAD_TIMEOUT_MS)
            # Original: print(f"{log_prefix} DEBUG: Attempting to set default timeout on page object...")
            page.set_default_timeout(PAGE_LOAD_TIMEOUT_MS)
            # Original: print(f"{log_prefix} DEBUG: Set default timeout.")
            page.set_default_navigation_timeout(PAGE_LOAD_TIMEOUT_MS)
            print(f"{log_prefix} Context and page created, default timeouts set.") # Original comment wording adapted

            # Apply stealth (Original section title)
            print(f"{log_prefix} Applying stealth...") # Original comment
            await stealth_async(page) 
            print(f"{log_prefix} Stealth applied.") # Original comment

            # --- Multi-hop Loop ---
            for hop_count in range(max_hops):
                hop_log_prefix = f"{log_prefix} [Hop {hop_count + 1}/{max_hops}]"
                print(f"{hop_log_prefix} Processing URL: {current_url_to_process}")

                parsed_current_url = urlparse(current_url_to_process)
                current_domain = parsed_current_url.netloc.replace('www.', '')
                site_config = SITE_SELECTORS.get(current_domain)

                if not site_config:
                    print(f"{hop_log_prefix} No config for domain '{current_domain}'. Assuming final player URL.")
                    final_player_url = current_url_to_process
                    break 

                if site_config.get("is_final_player_host"):
                    print(f"{hop_log_prefix} Domain '{current_domain}' is marked as final player host.")
                    final_player_url = current_url_to_process
                    break 

                # Navigate with better error handling (Original Comment for initial navigation)
                if page.url != current_url_to_process and not current_url_to_process.startswith("about:blank"):
                    print(f"{hop_log_prefix} Navigating to: {current_url_to_process}")
                    try:
                        # Consider changing wait_until based on site behavior, e.g., "load" or "networkidle"
                        response = await page.goto(current_url_to_process, wait_until="domcontentloaded") 
                        if response:
                            # Original: print(f"{log_prefix} Navigation complete (status: {response.status}).")
                            print(f"{hop_log_prefix} Nav to '{current_url_to_process}' complete (status: {response.status}).")
                            if not response.ok:
                                # Original: print(f"{log_prefix} WARNING: Navigation status code was {response.status}.")
                                print(f"{hop_log_prefix} WARN: Nav status {response.status} for {current_url_to_process}.")
                        else:
                            # Original: print(f"{log_prefix} Navigation completed but no response object returned.")
                            print(f"{hop_log_prefix} Nav to '{current_url_to_process}' complete (no response object).")
                    except PlaywrightError as nav_error:
                        # Original: print(f"{log_prefix} Navigation error: {nav_error}")
                        print(f"{hop_log_prefix} Nav error for {current_url_to_process}: {nav_error}")
                        if "net::ERR_INVALID_AUTH_CREDENTIALS" in str(nav_error): # Original check
                            # Original: print(f"{log_prefix} ERROR: Proxy authentication failed. Check your proxy credentials.")
                            # Original: raise Exception("Proxy authentication failed")
                            print(f"{hop_log_prefix} ERROR: Proxy auth failed. Check credentials.")
                        raise 
                    
                    # Sleep for movuna.xyz inspection
                    if "movuna.xyz" in current_url_to_process.lower(): # make domain check case-insensitive
                        print(f"{hop_log_prefix} PAUSING on {current_domain} for manual inspection (60 seconds)...")
                        #! <-------------- sleep right here
                        await asyncio.sleep(60) 
                        print(f"{hop_log_prefix} Resuming after pause...")
                    else:
                        # Standard wait for other pages if not movuna
                        await asyncio.sleep(random.uniform(2, 5)) # Wait for dynamic content

                else:
                    print(f"{hop_log_prefix} Already on or just processed URL: {page.url}. Skipping explicit navigation.")

                actions_for_domain = site_config.get("actions", [])
                if not actions_for_domain:
                    print(f"{hop_log_prefix} No actions for '{current_domain}', not final. Assuming current URL: {page.url}")
                    final_player_url = page.url
                    break

                next_url_from_actions: str | None = None

                for action_config in actions_for_domain:
                    action_type = action_config["type"]
                    action_log_prefix = f"{hop_log_prefix} Action [{action_type}]"

                    if action_type == "click":
                        # This section corresponds to "Step 1: Click the initial play button" in original logic
                        print(f"{action_log_prefix}: Initiating click.")
                        click_selectors = action_config["selectors"]
                        timeout_for_click = action_config.get("click_timeout_ms", CLICK_TIMEOUT_MS)
                        
                        click_successful = await find_and_click_element(page, click_selectors, timeout_for_click, log_prefix=action_log_prefix)
                        if not click_successful:
                            # Original: print(f"{log_prefix} Could not click initial play button. Cannot proceed.")
                            # Original: raise Exception("Failed to click initial play button.")
                            raise Exception(f"{action_log_prefix}: Click failed for selectors: {click_selectors}")
                        
                        post_click_wait_s_config = action_config.get("post_click_wait_s", (1.0, 3.0))
                        wait_duration = random.uniform(post_click_wait_s_config[0], post_click_wait_s_config[1])
                        # Original: print(f"{log_prefix} Initial click attempt finished. Waiting for iframe...")
                        # Original: await asyncio.sleep(random.uniform(3, 6))
                        # Now wait is configurable and specific to the action
                        print(f"{action_log_prefix}: Click successful. Waiting {wait_duration:.2f}s post-click.")
                        await asyncio.sleep(wait_duration)

                    elif action_type == "extract_iframe_src":
                        # This section corresponds to "Step 2: Find the iframe and extract src" in original logic
                        print(f"{action_log_prefix}: Initiating iframe src extraction.")
                        iframe_target_selector = action_config["iframe_selector"]
                        parent_elem_selector = action_config.get("parent_selector") # This will be None for movuna.xyz with your current SITE_SELECTORS
                        poll_timeout_ms_for_action = action_config.get("iframe_src_poll_timeout_ms", IFRAME_SRC_POLL_TIMEOUT_MS)

                        iframe_locator_obj: Locator | None = None
                        if parent_elem_selector:
                            # Original: print(f"{log_prefix} Locating iframe: {player_iframe_selector}") (adapted)
                            print(f"{action_log_prefix} Locating parent '{parent_elem_selector}' for iframe '{iframe_target_selector}'")
                            parent_element_loc = page.locator(parent_elem_selector).first
                            # Original: print(f"{log_prefix} Waiting up to {INTERACTION_TIMEOUT_SECONDS}s for iframe element to be attached...")
                            # Original: await iframe_locator.wait_for(state="attached", timeout=INTERACTION_TIMEOUT_SECONDS * 1000)
                            await parent_element_loc.wait_for(state="attached", timeout=INTERACTION_TIMEOUT_MS)
                            iframe_locator_obj = parent_element_loc.locator(iframe_target_selector).first
                        else:
                            # This path will be taken for movuna.xyz based on your current SITE_SELECTORS
                            print(f"{action_log_prefix} Locating iframe directly: {iframe_target_selector}")
                            iframe_locator_obj = page.locator(iframe_target_selector).first
                        
                        print(f"{action_log_prefix} Waiting for iframe element to be attached (timeout: {INTERACTION_TIMEOUT_MS}ms)...")
                        await iframe_locator_obj.wait_for(state="attached", timeout=INTERACTION_TIMEOUT_MS)
                        # Original: print(f"{log_prefix} Player iframe element found in DOM.")
                        print(f"{action_log_prefix} Iframe element found in DOM.")

                        # Original: print(f"{log_prefix} Polling up to {IFRAME_SRC_TIMEOUT_SECONDS}s for valid iframe src attribute...")
                        print(f"{action_log_prefix} Polling up to {poll_timeout_ms_for_action/1000:.1f}s for valid iframe src...")
                        start_time_iframe_poll = time.monotonic()
                        extracted_src_val: str | None = None 
                        while time.monotonic() - start_time_iframe_poll < (poll_timeout_ms_for_action / 1000):
                            # --- await the get_attribute call --- (Original Comment)
                            src_attr_val = await iframe_locator_obj.get_attribute("src")
                            # Check if src exists and looks like a valid HTTP/HTTPS URL (Original Comment)
                            if src_attr_val and urlparse(src_attr_val).scheme in ['http', 'https']:
                                # Resolve relative URLs if any (e.g. /path/to/iframe)
                                extracted_src_val = urlsplit(page.url)._replace(path=src_attr_val, query='', fragment='').geturl() if src_attr_val.startswith('/') else src_attr_val
                                print(f"{action_log_prefix} Found valid iframe src: {extracted_src_val}")
                                break # Exit loop once valid src is found (Original Comment)
                            await asyncio.sleep(0.5) # Check every half second (Original Comment)
                        
                        if not extracted_src_val:
                            # Check if the loop completed without finding the src (Original Comment)
                            # Original: print(f"{log_prefix} Timeout waiting for valid iframe src attribute within {IFRAME_SRC_TIMEOUT_SECONDS}s.")
                            # Original: raise Exception("Timeout waiting for iframe src attribute.")
                            raise Exception(f"{action_log_prefix} Timeout waiting for iframe src for selector '{iframe_target_selector}'.")
                        
                        next_url_from_actions = extracted_src_val
                        # Original: player_url_result = extracted_src (now assigned to next_url_from_actions)
                        # Original: print(f"{log_prefix} Successfully extracted player URL: {player_url_result}")
                        print(f"{action_log_prefix} Extracted next URL: {next_url_from_actions}")
                        # Important: Break from this domain's actions loop, proceed to next hop with this URL
                        # This assumes an iframe src extraction is the last significant action for that domain to get the *next* URL.
                        break 
                    
                    else:
                        print(f"{action_log_prefix} WARN: Unknown action type '{action_type}' for domain '{current_domain}'.")


                if next_url_from_actions:
                    current_url_to_process = next_url_from_actions
                    expected_domain_hint = site_config.get("next_expected_domain_hint")
                    if expected_domain_hint:
                        actual_next_domain_parsed = urlparse(current_url_to_process).netloc.replace('www.','')
                        if expected_domain_hint not in actual_next_domain_parsed:
                             print(f"{hop_log_prefix} WARN: Next URL domain '{actual_next_domain_parsed}' doesn't match hint '{expected_domain_hint}'.")
                else: 
                    if not site_config.get("is_final_player_host"):
                        print(f"{hop_log_prefix} No new URL extracted from '{current_domain}' actions and not a final host. Using current URL: {page.url}")
                    final_player_url = page.url 
                    break 

            if not final_player_url and hop_count == max_hops -1: 
                print(f"{log_prefix} Max hops ({max_hops}) reached. Last processed URL: {current_url_to_process}")
                final_player_url = current_url_to_process # Use the last URL processed as the result

        # --- Main Exception Handling --- (Original Section Comment)
        except PlaywrightTimeoutError as e:
            # Original: print(f"{log_prefix} Playwright Timeout Error: {e}")
            print(f"{log_prefix} FATAL: Playwright Timeout Error during execution: {e}") # Added "during execution" for clarity
            traceback.print_exc()
            final_player_url = None # Ensure result is None on failure (Original Comment)
        except PlaywrightError as e:  # Catch other Playwright-specific errors (Original Comment)
            # Original: print(f"{log_prefix} Playwright Error: {type(e).__name__} - {e}")
            print(f"{log_prefix} FATAL: Playwright Error during execution: {type(e).__name__} - {e}") # Added "during execution"
            traceback.print_exc()
            final_player_url = None  # Ensure result is None on failure (Original Comment)
        except Exception as e:
            # Catch any other general errors (Original Comment)
            # Original: print(f"{log_prefix} General Error in finder: {type(e).__name__} - {e}")
            print(f"{log_prefix} FATAL: General Error in finder: {type(e).__name__} - {e}")
            # if isinstance(e, TypeError): traceback.print_exc() # Print stack trace for TypeError (Original Comment)
            # traceback.print_exc() will be printed for all general exceptions now for better debugging
            traceback.print_exc()
            final_player_url = None  # Ensure result is None on failure (Original Comment)
        # --- End Main Exception Handling --- (Original Section Comment)

        finally:
            # Original: print(f"{log_prefix} Entering cleanup block...")
            print(f"{log_prefix} Entering cleanup block...")
            # Playwright handles closing related contexts/pages when browser is closed (Original Comment)
            # We only need to ensure browser.close() is called if browser was launched (Original Comment)
            if browser: 
                try:
                    # Check connection state synchronously before trying async close (Original Comment, adapted)
                    if browser.is_connected():
                        # Original: print(f"{log_prefix} Attempting to close browser...")
                        print(f"{log_prefix} Attempting to close browser...")
                        await browser.close()  # browser.close() is async and handles contexts/pages (Original Comment)
                        # Original: print(f"{log_prefix} Browser closed.")
                        print(f"{log_prefix} Browser closed.")
                    else:
                        # Original: print(f"{log_prefix} Browser already disconnected.")
                        print(f"{log_prefix} Browser already disconnected.")
                except Exception as browser_close_err:
                    print(f"{log_prefix} Error closing browser: {browser_close_err}")
            else:
                # Browser likely failed during launch if it's None here (Original Comment)
                print(f"{log_prefix} Browser object was not initialized or launch failed.")

            # Original: print(f"{log_prefix} Player URL finder finished.")
            print(f"{log_prefix} Player URL finder finished. Result: {final_player_url}")
            
        # Return the final result (None if any exception occurred) (Original Comment)
        return final_player_url