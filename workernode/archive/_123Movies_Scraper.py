#New
# src/scrapers/media_scraper.py
import time
import random
import re
import requests
# Keep uc for ChromeOptions if you prefer, or use seleniumwire's uc options
import undetected_chromedriver as uc
# --- MODIFIED IMPORT: Import the combined Chrome class from seleniumwire's integration ---
from seleniumwire.undetected_chromedriver import Chrome as SwUcChrome
# --- END MODIFIED IMPORT ---

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# --- MODIFIED IMPORT: Added specific exceptions ---
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    NoSuchWindowException,
    SessionNotCreatedException
)
# --- END MODIFIED IMPORT ---
from selenium.webdriver.common.action_chains import ActionChains
# Removed unused import: from seleniumwire.undetected_chromedriver import ChromeOptions

from src.config import settings
import os

def configure_driver(proxy_config=None):
    """Configures and returns Chrome options and Selenium Wire options."""
    # You can still use uc.ChromeOptions here if desired
    options = uc.ChromeOptions()
    # Standard options
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--start-maximized")

    # More robust fingerprint evasion
    options.add_argument('--disable-blink-features=AutomationControlled')

    # Randomize user agent slightly between sessions
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    options.add_argument('--lang=en-US,en;q=0.9')


    # --- START: Added code for uBlock Origin ---
    try:
        # Construct the path relative to this script file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(script_dir)) # Assumes src/scrapers/ structure
        # --- POTENTIAL PATH ISSUE: Check which path is correct for your structure ---
        # Option 1 (if manifest.json is directly in ublock_origin_unpacked):
        # ublock_base_path = os.path.join(project_root, 'extensions', 'ublock_origin_unpacked')
        # Option 2 (if manifest.json is inside the subfolder):
        ublock_base_path = os.path.join(project_root, 'extensions', 'ublock_origin_unpacked', 'uBlock-Origin-Lite-Chrome-Web-Store')
        # --- END POTENTIAL PATH ISSUE ---

        # Check if the directory and the manifest file exist
        manifest_path = os.path.join(ublock_base_path, 'manifest.json')
        if os.path.isdir(ublock_base_path) and os.path.exists(manifest_path):
            print(f"[Scraper] Found uBlock Origin extension at: {ublock_base_path}")
            # Load the unpacked extension
            options.add_argument(f'--load-extension={ublock_base_path}')
            # Optional: Disable other extensions except the one(s) loaded. Good practice.
            options.add_argument(f'--disable-extensions-except={ublock_base_path}')
            print("[Scraper] Added uBlock Origin loading arguments.")
        else:
            print(f"[Scraper] WARNING: uBlock Origin directory with manifest.json not found at '{ublock_base_path}'. Searched for '{manifest_path}'. Proceeding without ad blocker.")
            # Decide if you want to raise an error here if the extension is critical
            # raise FileNotFoundError(f"uBlock Origin directory with manifest.json not found at {ublock_base_path}")

    except Exception as e:
        print(f"[Scraper] WARNING: Failed to configure uBlock Origin - {e}")
    # --- END: Added code for uBlock Origin ---




    if settings.SCRAPER_HEADLESS:
        print("[Scraper] Configuring for HEADLESS mode.")
        options.add_argument('--headless=new')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

    # Selenium Wire options dictionary
    sw_options = {}
    if proxy_config and 'proxy' in proxy_config and 'https' in proxy_config['proxy']:
        # Ensure correct structure for selenium-wire options
        sw_options = {'proxy': proxy_config['proxy']}
        # Log only host/port if possible
        proxy_host_port = proxy_config['proxy']['https'].split('@')[-1]
        print(f"[Scraper] Configuring proxy via Selenium Wire: {proxy_host_port}")
        # Many streaming sites detect and block datacenter IPs
        # Residential proxies are recommended for production use
    elif proxy_config:
        print("[Scraper] WARNING: Proxy config provided but structure is incorrect or missing 'https' key.")


    return options, sw_options

def is_valid_m3u8(url):
    """Validate if URL contains actual M3U8 content."""
    try:
        # Use a session for potential keep-alive benefits
        with requests.Session() as session:
            # Add a common browser user-agent
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            response = session.get(url, timeout=10, headers=headers, stream=True) # Use stream=True to only download headers initially
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

            # Check content type first if available
            content_type = response.headers.get('Content-Type', '').lower()
            if 'mpegurl' in content_type or 'x-mpegurl' in content_type or 'vnd.apple.mpegurl' in content_type:
                 print(f"[Validator] Confirmed M3U8 via Content-Type: {content_type}")
                 return True

            # If content-type isn't definitive, check the first few lines of content
            content_snippet = ""
            bytes_read = 0
            max_bytes = 1024 # Read up to 1KB to find tags
            for chunk in response.iter_content(chunk_size=128):
                content_snippet += chunk.decode('utf-8', errors='ignore')
                bytes_read += len(chunk)
                if '#extm3u' in content_snippet.lower() or bytes_read >= max_bytes:
                    break

        content_lower = content_snippet.lower()
        is_m3u8 = ('#extm3u' in content_lower and
                   ('#ext-x-stream-inf' in content_lower or '#extinf' in content_lower))
        if is_m3u8:
            print(f"[Validator] Confirmed M3U8 via content tags.")
        return is_m3u8

    except requests.exceptions.RequestException as e:
        print(f"[Validator] Request failed for {url}: {e}")
        return False
    except Exception as e:
        print(f"[Validator] Unexpected error validating {url}: {e}")
        return False

def click_element_safely(driver, element, log_prefix=""):
    """Try multiple click methods to handle tricky elements."""
    methods = [
        ("Element Click", lambda: element.click()),
        ("Action Chain Click", lambda: ActionChains(driver).move_to_element(element).click().perform()),
        ("JavaScript Click", lambda: driver.execute_script("arguments[0].click();", element))
    ]

    last_exception = None
    for name, method in methods:
        try:
            print(f"{log_prefix} Trying click method: {name}...")
            method()
            # Short pause after successful click to allow UI update
            time.sleep(random.uniform(0.5, 1.0))
            # Optional: Add a check here if the click had the desired effect (e.g., element disappeared)
            print(f"{log_prefix} Click method '{name}' succeeded")
            return True
        except StaleElementReferenceException:
            print(f"{log_prefix} Click method '{name}' failed: StaleElementReferenceException. Element may have changed.")
            return False # Stop trying if element is stale
        except Exception as e:
            print(f"{log_prefix} Click method '{name}' failed: {type(e).__name__}")
            last_exception = e

    print(f"{log_prefix} All click methods failed.")
    if last_exception:
         print(f"{log_prefix} Last error: {last_exception}")
    return False

def handle_iframes(driver, wait, log_prefix=""):
    """Switch to iframes that might contain the video player."""
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
    except Exception as e:
        print(f"{log_prefix} Error finding iframes: {e}")
        return False # Cannot proceed if finding elements fails

    if not iframes:
        print(f"{log_prefix} No iframes found on the page.")
        return False

    print(f"{log_prefix} Found {len(iframes)} iframes. Checking each...")
    original_window = driver.current_window_handle # Keep track

    for i, iframe_element in enumerate(iframes):
        try:
            # Check if iframe is visible, tiny iframes are often ads/trackers
            if iframe_element.is_displayed() and iframe_element.size['width'] > 50 and iframe_element.size['height'] > 50:
                print(f"{log_prefix} Switching to potentially relevant iframe {i+1}...")
                driver.switch_to.frame(iframe_element)
                time.sleep(random.uniform(0.5, 1.0)) # Short pause after switch

                # Look for video elements or common player IDs/classes within this iframe
                # Use find_elements which doesn't raise error if not found
                video_elements = driver.find_elements(By.TAG_NAME, "video")
                # More specific player selectors
                player_divs = driver.find_elements(By.CSS_SELECTOR, "div[id*='player'], div[class*='player'], .video-js, #jwplayer")

                if video_elements or player_divs:
                    print(f"{log_prefix} Found potential video container or player element in iframe {i+1}. Staying in this frame.")
                    return True # Successfully switched to a promising iframe

                print(f"{log_prefix} No video/player elements found in iframe {i+1}. Switching back.")
                driver.switch_to.default_content()
                time.sleep(random.uniform(0.3, 0.7))
            else:
                 print(f"{log_prefix} Skipping hidden or small iframe {i+1}.")

        except NoSuchElementException:
            print(f"{log_prefix} Iframe {i+1} seems to have disappeared (NoSuchElementException). Switching back.")
            driver.switch_to.default_content()
        except StaleElementReferenceException:
             print(f"{log_prefix} Iframe {i+1} became stale. Switching back.")
             driver.switch_to.default_content()
        except Exception as e:
            print(f"{log_prefix} Error handling iframe {i+1}: {type(e).__name__}. Switching back.")
            # Ensure we always switch back in case of unexpected error
            try:
                 driver.switch_to.default_content()
            except Exception:
                 print(f"{log_prefix} Could not switch back to default content from iframe {i+1}.")
                 # May need to restart driver if context is lost

    print(f"{log_prefix} No usable video iframes found after checking all. Remaining in default content.")
    return False # Did not switch or stay in an iframe

def handle_common_overlay_patterns(driver, wait, log_prefix=""):
    """Try to handle common overlay patterns seen on streaming sites."""
    # Common patterns for play buttons, overlays, and ads
    # Prioritize more specific patterns first
    patterns = [
        # Specific player buttons
        {"type": "SELECTOR", "value": ".jwplayer .jw-icon-playback", "desc": "JWPlayer Play button"},
        {"type": "SELECTOR", "value": ".video-js .vjs-big-play-button", "desc": "VideoJS Play button"},
        {"type": "SELECTOR", "value": ".ytp-large-play-button", "desc": "YouTube-style Play button"},
        # Generic play buttons
        {"type": "SELECTOR", "value": "button[class*='play'], button[id*='play'], div[class*='play-button']", "desc": "Play button element"},
        {"type": "XPATH", "value": "//*[contains(@aria-label, 'Play') or contains(@title, 'Play')]", "desc": "Play button (ARIA/Title)"},
        # Overlays
        {"type": "SELECTOR", "value": "div[class*='overlay'][style*='display: block'], div[id*='overlay'][style*='display: block']", "desc": "Visible Overlay"},
        # Close buttons (often on ads or overlays)
        {"type": "SELECTOR", "value": "[id*='close'][style*='display: block'], [class*='close'][style*='display: block']", "desc": "Visible Close button"},
        {"type": "XPATH", "value": "//div[contains(@class, 'ad')]//*[contains(@class, 'close') or contains(text(), 'Close') or @aria-label='Close']", "desc": "Ad Close button"},
    ]

    clicked_something = False
    for pattern in patterns:
        try:
            print(f"{log_prefix} Looking for '{pattern['desc']}': {pattern['value']}")
            elements = []
            attempts = 0
            # Retry finding elements briefly in case they appear slowly
            while attempts < 2 and not elements:
                if pattern["type"] == "SELECTOR":
                    elements = driver.find_elements(By.CSS_SELECTOR, pattern["value"])
                else:  # XPATH
                    elements = driver.find_elements(By.XPATH, pattern["value"])
                if not elements and attempts == 0:
                     time.sleep(0.5) # Brief pause before retry
                attempts += 1

            if elements:
                print(f"{log_prefix} Found {len(elements)} potential '{pattern['desc']}' elements")
                # Iterate through found elements
                for i, element in enumerate(elements):
                     try:
                         # Check visibility robustly
                         if element.is_displayed():
                             print(f"{log_prefix} Element {i+1} ('{pattern['desc']}') is visible. Attempting to click...")
                             if click_element_safely(driver, element, log_prefix):
                                 print(f"{log_prefix} Successfully clicked '{pattern['desc']}'")
                                 # Wait longer after a successful click to allow state changes/loading
                                 time.sleep(random.uniform(3, 5))
                                 clicked_something = True
                                 # Consider returning True immediately after the first successful click
                                 # if you only expect one primary interaction
                                 # return True
                             else:
                                 print(f"{log_prefix} Failed to click visible element {i+1} ('{pattern['desc']}')")
                         # else:
                         #    print(f"{log_prefix} Element {i+1} ('{pattern['desc']}') found but not visible.")
                     except StaleElementReferenceException:
                         print(f"{log_prefix} Element {i+1} ('{pattern['desc']}') became stale during check.")
                         continue # Move to the next element if this one is gone
            # else:
            #    print(f"{log_prefix} No elements found for '{pattern['desc']}'")

        except Exception as e:
            print(f"{log_prefix} Error searching for '{pattern['desc']}' ({pattern['value']}): {type(e).__name__}")

    # Return True if any click was successful during the pattern search
    return clicked_something


async def scrape_for_m3u8(target_url: str, job_id: str, proxy_config: dict | None = None) -> str | None:
    """
    Enhanced scraper for M3U8 URLs from streaming sites using selenium-wire's uc integration,
    with better interception, overlay handling, iframe support, and content validation.
    Returns the M3U8 URL string or None if not found.
    """
    log_prefix = f"[Scraper Job {job_id}]"
    print(f"{log_prefix} Starting enhanced scrape for: {target_url}")
    m3u8_url = None
    driver = None # Initialize driver to None

    options, sw_options = configure_driver(proxy_config)

    script_dir = os.path.dirname(__file__)
    project_root = os.path.dirname(os.path.dirname(script_dir))
    driver_path_explicit = os.path.join(project_root, 'drivers', 'chromedriver.exe')

    driver_executable = None # Default to None (uc handles download)
    if os.path.exists(driver_path_explicit):
        print(f"{log_prefix} Attempting to use explicit driver path: {driver_path_explicit}")
        driver_executable = driver_path_explicit
    else:
        print(f"{log_prefix} INFO: Explicit driver not found at '{driver_path_explicit}'. Letting undetected-chromedriver manage driver download/path.")


    try:
        print(f"{log_prefix} Initializing seleniumwire undetected_chromedriver...")
        # --- MODIFIED DRIVER INSTANTIATION ---
        driver = SwUcChrome(   # Use the imported class from seleniumwire.undetected_chromedriver
            options=options,
            seleniumwire_options=sw_options,
            driver_executable_path=driver_executable # Pass explicit path or None
        )
        # --- END MODIFIED DRIVER INSTANTIATION ---

        print(f"{log_prefix} Driver initialized.")
        # Set timeouts
        driver.set_page_load_timeout(settings.SCRAPER_TIMEOUT_SECONDS)
        driver.implicitly_wait(5) # Small implicit wait can sometimes help stabilize element finding
        wait = WebDriverWait(driver, 20) # Slightly shorter explicit wait default

        print(f"{log_prefix} Navigating to {target_url}...")
        driver.get(target_url)

        # Wait for page body tag to ensure basic page structure is loaded
        try:
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print(f"{log_prefix} Page loaded. Body tag found.")
        except TimeoutException:
            print(f"{log_prefix} Warning: Timed out waiting for body tag. Page might be malformed or very slow. Continuing anyway...")
            # Check if the URL is still the same, maybe a redirect failed?
            if driver.current_url != target_url:
                 print(f"{log_prefix} URL changed to: {driver.current_url}. Possible redirect issue.")
                 # Consider failing here if the initial load seems broken
                 # raise TimeoutException("Page failed to load initial body or redirected unexpectedly.")


        # Add variable delay after load for scripts to potentially run
        delay = random.uniform(3, 6)
        print(f"{log_prefix} Adding post-navigation delay of {delay:.1f}s...")
        time.sleep(delay)

        # More realistic human scrolling
        print(f"{log_prefix} Simulating natural scrolling behavior...")
        try:
            scroll_amount = random.randint(300, 600)
            driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.8, 1.5))

            # Sometimes scroll back up slightly
            if random.random() > 0.7:
                driver.execute_script(f"window.scrollBy(0, -{random.randint(50, 150)});")
                time.sleep(random.uniform(0.5, 1))
        except Exception as scroll_err:
             print(f"{log_prefix} Warning: Error during scrolling: {scroll_err}")


        # ----- Handle iframes if present -----
        # handle_iframes will switch context if successful
        switched_to_iframe = handle_iframes(driver, wait, log_prefix)
        if switched_to_iframe:
            print(f"{log_prefix} Working within iframe content now")
            # Re-initialize wait context for the iframe if needed, though usually not required
            # wait = WebDriverWait(driver, 20)
        else:
             print(f"{log_prefix} Staying in main page content.")


        # ----- Handle common overlay/play button patterns -----
        # Reduced interaction attempts, often only one click is needed
        interaction_attempts = 2
        overlay_handled = False
        for attempt in range(interaction_attempts):
            print(f"{log_prefix} Looking for player elements (attempt {attempt+1}/{interaction_attempts})...")
            if handle_common_overlay_patterns(driver, wait, log_prefix):
                overlay_handled = True
                print(f"{log_prefix} Successfully interacted with player element on attempt {attempt+1}")
                # Wait a bit longer after successful interaction for network activity
                print(f"{log_prefix} Waiting after interaction...")
                time.sleep(random.uniform(6, 10)) # Increased wait
                break # Exit loop once handled
            elif attempt < interaction_attempts - 1: # Don't wait after the last attempt
                print(f"{log_prefix} No interactable elements found yet, waiting before next attempt...")
                time.sleep(random.uniform(2, 4))


        if not overlay_handled:
            print(f"{log_prefix} No standard player elements found/clicked after {interaction_attempts} attempts. Waiting for potential autoplay or delayed load...")
            # Increased wait if no interaction occurred, maybe autoplay or scripts are slow
            time.sleep(random.uniform(10, 15))


        # ----- Capture and filter for M3U8 URLs -----
        print(f"{log_prefix} Scanning network requests for M3U8 content...")

        m3u8_candidates = []
        try:
            # --- MODIFIED REQUEST ACCESS ---
            # Access the requests attribute from the selenium-wire driver object
            captured_requests = driver.requests # Get the list of requests captured so far
            # --- END MODIFIED REQUEST ACCESS ---
            print(f"{log_prefix} Analyzing {len(captured_requests)} captured network requests...")

            for request in captured_requests:
                # Check if URL is valid and contains potential M3U8 indicators
                if request and request.url and isinstance(request.url, str) and (
                    ('.m3u8' in request.url.lower()) or
                    ('/master.' in request.url.lower()) or
                    ('/playlist.' in request.url.lower()) or
                    ('/manifest(format=m3u8' in request.url.lower()) # Add specific formats if seen
                   ):

                    status_code = 'N/A'
                    content_type = 'unknown'
                    timestamp = time.time() # Default timestamp

                    # Try to get response details safely
                    if request.response:
                        status_code = request.response.status_code
                        content_type = request.response.headers.get('Content-Type', 'unknown')
                        if hasattr(request.response, 'date') and request.response.date:
                            timestamp = request.response.date

                        # Log only potentially useful candidates (status 2xx or redirects 3xx maybe)
                        if status_code and (200 <= status_code < 400):
                             print(f"{log_prefix} Potential stream URL: {request.url}")
                             print(f"{log_prefix} - Status: {status_code}, Content-Type: {content_type}")
                             m3u8_candidates.append({
                                'url': request.url,
                                'content_type': content_type,
                                'timestamp': timestamp,
                             })
                    # else:
                        # Optionally log requests without responses if needed for debug
                        # print(f"{log_prefix} Found potential M3U8 URL pattern but no response captured: {request.url}")

            # Clear requests after processing
            if hasattr(driver, 'requests'): # Check attribute exists before deleting
                del driver.requests
                print(f"{log_prefix} Cleared captured network requests ({len(captured_requests)} processed).")

        except AttributeError:
            print(f"{log_prefix} FATAL: driver object does not have 'requests' attribute. Check driver initialization (ensure seleniumwire.uc is used).")
            # Re-raise immediately as this is a fundamental setup issue
            raise
        except Exception as req_err:
            print(f"{log_prefix} Error processing network requests: {type(req_err).__name__} - {req_err}")


        # --- Filtering and Validation ---
        valid_candidates = []
        print(f"{log_prefix} Found {len(m3u8_candidates)} potential M3U8 candidates from network traffic.")
        for candidate in m3u8_candidates:
            # Prioritize URLs explicitly ending in .m3u8
            if '.m3u8' in candidate['url'].lower().split('?')[0]: # Check before query params
                print(f"{log_prefix} Validating M3U8 content for: {candidate['url']}")
                if is_valid_m3u8(candidate['url']):
                    print(f"{log_prefix} ✓ Confirmed valid M3U8 content via request.")
                    valid_candidates.append(candidate)
                else:
                    print(f"{log_prefix} ✗ Failed M3U8 content validation via request for: {candidate['url']}")
            # Keep other potential manifests but maybe rank them lower if needed
            # else:
            #    valid_candidates.append(candidate) # Or handle non-.m3u8 manifests differently

        # Select best candidate (prefer most recent valid .m3u8)
        if valid_candidates:
            # Sort by timestamp (newest first)
            sorted_candidates = sorted(valid_candidates, key=lambda x: x.get('timestamp', 0), reverse=True)
            # Prefer candidates that passed validation
            best_candidate = next((c for c in sorted_candidates if '.m3u8' in c['url'].lower().split('?')[0]), None)
            if best_candidate:
                 m3u8_url = best_candidate['url']
                 print(f"{log_prefix} ✓✓✓ Selected validated M3U8 URL: {m3u8_url}")
            else:
                 # Fallback to most recent if no validated .m3u8 found
                 m3u8_url = sorted_candidates[0]['url']
                 print(f"{log_prefix} ✓✓✓ Selected M3U8 URL (fallback, validation failed/skipped): {m3u8_url}")

        else:
            print(f"{log_prefix} ✗ No valid/usable M3U8 candidates found in initial network traffic.")

            # Fallback: Check page source if no network hits
            if not m3u8_url:
                 print(f"{log_prefix} Trying fallback: Searching page source for M3U8 URLs...")
                 try:
                     page_source = driver.page_source
                     # Refined regex to avoid javascript variables, look for common patterns
                     hls_matches = re.findall(r'[\'"](https?://[^\'"\s]+\.m3u8[^\'"\s]*)[\'"]', page_source, re.IGNORECASE)
                     if hls_matches:
                         print(f"{log_prefix} Found {len(hls_matches)} potential M3U8 URLs in page source.")
                         # Deduplicate
                         unique_matches = list(dict.fromkeys(hls_matches))
                         for url in unique_matches:
                             print(f"{log_prefix} Validating source URL: {url}")
                             if is_valid_m3u8(url):
                                 m3u8_url = url
                                 print(f"{log_prefix} ✓ Selected valid M3U8 from page source: {m3u8_url}")
                                 break # Take the first valid one found in source
                         if not m3u8_url:
                              print(f"{log_prefix} ✗ No validated M3U8 URLs found in page source.")
                     else:
                          print(f"{log_prefix} No M3U8 patterns found in page source.")
                 except Exception as source_err:
                      print(f"{log_prefix} Error getting/parsing page source: {source_err}")


    # --- Refined Exception Handling ---
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException, NoSuchWindowException) as e:
        print(f"{log_prefix} Selenium interaction error during scraping: {type(e).__name__} - {e}")
        if driver: save_debug_screenshot(driver, f"debug_selenium_error_{job_id}.png", log_prefix)
        raise # Re-raise to indicate failure to Celery
    except SessionNotCreatedException as e:
        print(f"{log_prefix} CRITICAL: Failed to create browser session: {e}")
        # No screenshot possible as driver didn't start
        raise # Re-raise critical failure
    except Exception as e:
        # Catch AttributeErrors specifically if they relate to driver setup
        if isinstance(e, AttributeError) and 'driver' in locals() and driver is None:
             print(f"{log_prefix} CRITICAL: Driver object likely not initialized correctly. Error: {e}")
        else:
             print(f"{log_prefix} Unexpected general error during scraping: {type(e).__name__} - {e}")
        # Save screenshot if driver exists
        if 'driver' in locals() and driver: save_debug_screenshot(driver, f"debug_general_error_{job_id}.png", log_prefix)
        raise # Re-raise general exceptions
    # --- END Refined Exception Handling ---
    finally:
        if 'driver' in locals() and driver:
            print(f"{log_prefix} Quitting WebDriver.")
            # Graceful quit with checks
            try:
                driver.quit()
            except (OSError, ImportError) as quit_err: # Catch potential errors during uc quit specifically
                 print(f"{log_prefix} Error during driver.quit() (expected with uc sometimes): {type(quit_err).__name__} - {quit_err}. Process might already be terminated.")
            except Exception as E:
                 print(f"{log_prefix} Unexpected error during driver.quit(): {type(E).__name__} - {E}. Process might already be terminated.")

    # --- Modified Return Logic ---
    if not m3u8_url:
        print(f"{log_prefix} ✗✗✗ No M3U8 URL ultimately extracted after all attempts.")
        # Return None to indicate failure without raising an exception that Celery might retry indefinitely
        # If you WANT retries on failure, raise ValueError here.
        # raise ValueError("M3U8 URL not found after enhanced scraping attempt.")
        return None
    # --- END Modified Return Logic ---

    print(f"{log_prefix} Success! Returning M3U8 URL: {m3u8_url}")
    return m3u8_url

# Helper function for saving screenshots to avoid repetition
def save_debug_screenshot(driver, filename, log_prefix):
    """Saves a screenshot if the driver object is valid."""
    if driver:
        try:
            driver.save_screenshot(filename)
            print(f"{log_prefix} Saved debug screenshot to {filename}")
        except Exception as screen_err:
            print(f"{log_prefix} Could not save screenshot: {type(screen_err).__name__} - {screen_err}")