# src/scrapers/media_scraper.py
import time
import random
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from seleniumwire.undetected_chromedriver import ChromeOptions # Import ChromeOptions from UDC with Wire

from src.config import settings # Import shared settings
import os # Import os module

def configure_driver(proxy_config=None):
    """Configures and returns Chrome options and Selenium Wire options."""
    options = uc.ChromeOptions()
    # Standard options
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-popup-blocking')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument("--start-maximized") # May help with layout issues
    # User agent spoofing (replace with a current, realistic one)
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36') # <-- Consider updating this UA string too
    options.add_argument('--lang=en-US,en;q=0.9') # Set language

    if settings.SCRAPER_HEADLESS:
        print("[Scraper] Configuring for HEADLESS mode.")
        options.add_argument('--headless=new') # Use the new headless mode
        options.add_argument('--disable-gpu')
        # options.add_argument('--window-size=1920,1080') # Set virtual window size

    # Selenium Wire options dictionary
    sw_options = {}
    if proxy_config:
        print(f"[Scraper] Configuring proxy via Selenium Wire: {proxy_config['proxy']['https'].split('@')[1]}") # Don't log user/pass
        sw_options.update(proxy_config)
        # Depending on proxy provider, might need to disable cert verification
        # sw_options['verify_ssl'] = False

    # Add experimental options that undetected-chromedriver uses/patches
    # options.add_experimental_option(
    #     "excludeSwitches", ["enable-automation", "enable-logging"]
    # )
    # options.add_experimental_option('useAutomationExtension', False)

    return options, sw_options





async def scrape_for_m3u8(target_url: str, job_id: str, proxy_config: dict | None = None) -> str | None:
    """
    Attempts to scrape an M3U8 URL from the target page using Selenium + UDC + Wire.
    Includes basic humanization and network interception.
    Returns the M3U8 URL string if found, otherwise None.
    """
    log_prefix = f"[Scraper Job {job_id}]"
    print(f"{log_prefix} Starting scrape for: {target_url}")
    m3u8_url = None
    driver = None
    
      

    options, sw_options = configure_driver(proxy_config)
      
    script_dir = os.path.dirname(__file__) # Gets directory of media_scraper.py
    project_root = os.path.dirname(os.path.dirname(script_dir)) # Up two levels to worker_node_py
    driver_path = os.path.join(project_root, 'drivers', 'chromedriver.exe')
    print(f"{log_prefix} Attempting to use explicit driver path: {driver_path}")
    
    
    if not os.path.exists(driver_path):
         print(f"{log_prefix} ERROR: ChromeDriver not found at specified path: {driver_path}")
         raise FileNotFoundError(f"ChromeDriver not found at {driver_path}")

    # --- ADDED: Define placeholder for path (keeping previous fix attempt, remove if not needed) ---
    # driver_path = os.path.join(os.path.dirname(__file__), '..', '..', 'drivers', 'chromedriver.exe')
    # print(f"{log_prefix} Using explicit driver path (if path exists): {driver_path}")


   

    try:
        print(f"{log_prefix} Initializing undetected_chromedriver with explicit driver path...")
        driver = uc.Chrome(
            options=options,
            seleniumwire_options=sw_options,
            # *** USE THE EXPLICIT PATH ***
            driver_executable_path=driver_path
            # version_main=YOUR_CHROME_MAJOR_VERSION # Can usually be omitted when using driver_executable_path
        )
        # *** End Modification ***

        print(f"{log_prefix} Driver initialized.") # Add log after init
        driver.set_page_load_timeout(settings.SCRAPER_TIMEOUT_SECONDS // 2) # Timeout for page load
        wait = WebDriverWait(driver, 25) # Default explicit wait timeout

        print(f"{log_prefix} Navigating to {target_url}...")
        driver.get(target_url)
        print(f"{log_prefix} Navigation initiated (driver.get returned). Waiting for full page load state...")
        # Add a more specific wait after navigation if needed, e.g., wait for body tag
        # wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        # print(f"{log_prefix} Body tag located.")

        # Optional: Add slight random delay after load appears complete
        print(f"{log_prefix} Adding post-navigation delay...")
        time.sleep(random.uniform(2, 4))

        # --- Simulate Human Interaction ---
        # ... (Keep scrolling logic) ...
        print(f"{log_prefix} Simulating minimal interaction (scrolling)...")
        driver.execute_script("window.scrollBy(0, Math.floor(document.body.scrollHeight * 0.1));")
        time.sleep(random.uniform(0.5, 1.5))
        driver.execute_script("window.scrollBy(0, Math.floor(document.body.scrollHeight * 0.1));")
        time.sleep(random.uniform(1, 2))


        # --- Wait for Player/Click Play ---
        # !!! CRITICAL: Replace with the ACTUAL selector for the play button/overlay !!!
        play_button_selector = "#video-container .play-button-class" # <-- MAKE SURE THIS IS CORRECT FOR YOUR SITE
        print(f"{log_prefix} Looking for play button: {play_button_selector}...")

        try:
            play_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, play_button_selector)))
            print(f"{log_prefix} Play button found. Simulating click...")
            driver.execute_script("arguments[0].scrollIntoView({ block: 'center' });", play_button)
            time.sleep(random.uniform(0.3, 0.8))
            play_button.click()
            print(f"{log_prefix} Play button clicked. Waiting for network requests...")
            time.sleep(random.uniform(4, 7))
        except TimeoutException:
            print(f"{log_prefix} Play button ({play_button_selector}) not found or not clickable within timeout. Assuming auto-play or different trigger.")
        except NoSuchElementException:
             print(f"{log_prefix} Play button ({play_button_selector}) element does not exist.")
        except Exception as e:
            print(f"{log_prefix} Error clicking play button: {e}")


        # --- Intercept and Find M3U8 ---
        # ... (Keep network request checking logic) ...
        print(f"{log_prefix} Checking captured network requests for M3U8...")
        time.sleep(2)
        possible_urls = []
        # Use driver.iter_requests() for potentially large number of requests
        for request in driver.iter_requests():
             if '.m3u8' in request.url:
                 # Filter more strictly if necessary (check response code and maybe content type)
                status_code = request.response.status_code if request.response else 'N/A'
                content_type = request.response.headers['Content-Type'] if request.response and 'Content-Type' in request.response.headers else 'N/A'
                print(f"{log_prefix} ---> Potential M3U8: {request.url} (Status: {status_code}, Type: {content_type})")
                 # Example stricter check:
                 # if status_code == 200 and ('mpegurl' in content_type or 'x-mpegurl' in content_type):
                 #     possible_urls.append(request.url)
                if status_code == 200: # Simpler check for now
                      possible_urls.append(request.url)

        # Clear requests after processing to free memory
        del driver.requests

        if possible_urls:
            m3u8_url = possible_urls[-1] # Assume last one is most relevant for now
            print(f"{log_prefix} Selected M3U8 URL: {m3u8_url}")
        else:
            print(f"{log_prefix} No M3U8 URL with status 200 found.")
            # driver.save_screenshot(f"debug_screenshot_job_{job_id}.png")


    except TimeoutException as e:
        print(f"{log_prefix} Timeout error during scraping: {e}")
        # Optionally take screenshot on timeout
        # try: driver.save_screenshot(f"timeout_screenshot_{job_id}.png")
        # except: pass
        raise  # Re-raise to fail the Celery task
    except Exception as e:
        print(f"{log_prefix} Unexpected error during scraping: {e}")
        # Optionally take screenshot on error
        # try: driver.save_screenshot(f"error_screenshot_{job_id}.png")
        # except: pass
        raise # Re-raise to fail the Celery task
    finally:
        if driver:
            print(f"{log_prefix} Quitting WebDriver.")
            driver.quit()

    if not m3u8_url:
        print(f"{log_prefix} No M3U8 URL ultimately extracted.")
        # Optionally raise specific error type?
        raise ValueError("M3U8 URL not found after scraping attempt.")


    return m3u8_url