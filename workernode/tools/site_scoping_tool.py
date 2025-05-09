# tools/site_scoping_tool.py

import asyncio
import os
import sys
import time # Make sure time is imported
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError, Page, Browser, BrowserContext, Error as PlaywrightError
import argparse
import traceback
from urllib.parse import urlparse, urlsplit, urlunparse
from dotenv import load_dotenv

# --- Load .env file FIRST ---
# This searches for .env in current or parent directories relative to this script
# It makes os.getenv work as expected later
load_dotenv()
print("[SiteScoper] Attempted to load environment variables from .env file.")
# --- End Load .env ---


# --- Configuration Specific to this Scoping Tool ---

# Define settings class to read from environment variables
class ToolSettings:
    SCRAPER_HEADLESS = False # Hardcoded to False for this tool

    #PROXY_ENABLED = os.getenv("PROXY_ENABLED", "false").lower() == "true" #? Sets proxy to On
    PROXY_ENABLED = False


    # Read proxy details from environment variables IF proxy is enabled
    _proxy_user = os.getenv("PROXY_USER") if PROXY_ENABLED else None
    _proxy_pass = os.getenv("PROXY_PASS") if PROXY_ENABLED else None
    _proxy_host = os.getenv("PROXY_HOST") if PROXY_ENABLED else None
    _proxy_port = os.getenv("PROXY_PORT") if PROXY_ENABLED else None
    _proxy_scheme = os.getenv("PROXY_TYPE", "http").lower() # Use http as default scheme

    # Construct the Playwright proxy dictionary IF all details are present
    PLAYWRIGHT_PROXY_CONFIG = None # Initialize as class attribute
    _proxy_fully_configured = False # Internal flag
    if PROXY_ENABLED and _proxy_user and _proxy_pass and _proxy_host and _proxy_port:
        PLAYWRIGHT_PROXY_CONFIG = {
            "server": f"{_proxy_scheme}://{_proxy_host}:{_proxy_port}",
            "username": _proxy_user,
            "password": _proxy_pass
        }
        _proxy_fully_configured = True # Mark as configured
        # Logging moved to where settings are instantiated or used for clarity
    elif PROXY_ENABLED:
        # Force disable if details are missing - do this check AFTER instantiation
        pass # Defer final decision until after instantiation
    # --- End Settings Defined within Class ---



# --- Instantiate the settings object ---
settings = ToolSettings()

# --- Log Proxy Status After Instantiation ---
# Moved this block to the top level, right after creating the settings instance
if settings.PROXY_ENABLED: # Check if initially enabled by .env
    if settings.PLAYWRIGHT_PROXY_CONFIG: # Check if config was successfully built
         print(f"[ToolSettings] Proxy ENABLED and configured via .env: Server={settings.PLAYWRIGHT_PROXY_CONFIG['server']}, User={settings._proxy_user}")
    else:
        # If enabled in .env but details were missing, log warning and force disable
        print("[ToolSettings] WARNING: PROXY_ENABLED is true in .env, but required details (USER, PASS, HOST, PORT) are missing or incomplete. Disabling proxy for this run.")
        settings.PROXY_ENABLED = False # Ensure consistency for the rest of the script
else:
    print("[ToolSettings] Proxy DISABLED (based on .env or missing details).")
# --- End Proxy Status Logging ---


# --- TARGET_SITES, ANTI_DEBUG_JS_FILE_PATH remain the same ---
TARGET_SITES = {
    "123movies": "https://ww19.0123movie.net/movie/alien-romulus-1630857469.html",
    "movuna": "https://movuna.xyz/watch/?v21#MThhcDB4QmRHQ3BKemRlclhZWWtucU9uakJFbXdORFNmdmpuN284WmZzdGdLMnNBYlo0U3hPVHVmY1QyZmtvRjdaV2FDWkp2OVc0PQ",
    "mcloud": "https://mcloud.vvid30c.site/watch/?v41#L0NYeWkvVGpZZVRKNmhWOHZ0TWlmTGpDUTNML0ErRVNkaUROMSt1SkdoQm9tL3IwMUtxMEhoTGlscjhud2lvM1drcjZXZ3Y1blNvPQ",
    "vidsrc": "https://vidsrc.xyz/embed/movie/1190012",
    "test1": "https://www.bing.com/search?pglt=299&q=clause+dastuffenburg&cvid=d433d4be3c4e4e4e993c570b23484018&gs_lcrp=EgRlZGdlKgYIABBFGDkyBggAEEUYOdIBCDcwMjNqMGoxqAIIsAIB&FORM=ANNTA1&PC=ASTS"
}
ANTI_DEBUG_JS_FILE_PATH = os.path.join(os.path.dirname(__file__), "anti_debug_snippets.js")


# --- Define Browser Launch Arguments using the settings instance ---
# This logic block now correctly references settings.SCRAPER_HEADLESS
if not settings.SCRAPER_HEADLESS: # Access the attribute from the instance
    print("[Config] Setting launch args for HEADFUL mode (Tool Default).")
    BROWSER_LAUNCH_ARGS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        # '--disable-gpu', # Keep GPU enabled for headful unless issues arise
        '--start-maximized',
        '--disable-infobars',
        '--disable-popup-blocking',
        '--disable-blink-features=AutomationControlled',
        # '--ignore-certificate-errors', # Only if needed
    ]
else:
    # This branch won't be hit with current ToolSettings class, but kept for structure
    print("[Config] Setting launch args for HEADLESS mode.")
    BROWSER_LAUNCH_ARGS = [
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--disable-blink-features=AutomationControlled',
    ]

# --- Helper function: save_debug_screenshot_pw (Keep as before) ---
async def save_debug_screenshot_pw(page: Page | None, filename: str, log_prefix: str):
     # ... (implementation remains the same) ...
    if page and not page.is_closed():
        try:
            output_dir = os.path.dirname(filename);
            if output_dir and not os.path.exists(output_dir): os.makedirs(output_dir, exist_ok=True) # Create dir if needed
            await page.screenshot(path=filename, full_page=True)
            print(f"{log_prefix} Saved debug screenshot to {filename}")
        except Exception as screen_err: print(f"{log_prefix} Could not save screenshot: {type(screen_err).__name__} - {screen_err}")
    else: print(f"{log_prefix} Cannot save screenshot, page object is None or closed.")

# --- async def scope_site(...) function remains the same ---
# It correctly uses settings.PROXY_ENABLED and settings.PLAYWRIGHT_PROXY_CONFIG now
async def scope_site(target_url: str, ublock_dir: str | None, anti_debug_script_content: str | None):
    # ... (Function body remains the same - uses settings.PROXY_ENABLED, etc.) ...
    log_prefix = "[SiteScoper]"
    print(f"{log_prefix} Scoping URL: {target_url}")
    browser: Browser | None = None

    async with async_playwright() as p:
        try:
            browser_args = list(BROWSER_LAUNCH_ARGS)
            if ublock_dir:
                browser_args.extend([ f'--disable-extensions-except={ublock_dir}', f'--load-extension={ublock_dir}' ])
                print(f"{log_prefix} Added uBlock launch arguments.")
            else: print(f"{log_prefix} No uBlock Origin path provided.")

            # --- Use Proxy from ToolSettings instance ---
            playwright_proxy = None
            # Use the potentially updated settings.PROXY_ENABLED value
            if settings.PROXY_ENABLED and settings.PLAYWRIGHT_PROXY_CONFIG:
                playwright_proxy = settings.PLAYWRIGHT_PROXY_CONFIG
                # Logging already done when settings instance was created
            elif settings.PROXY_ENABLED and not settings.PLAYWRIGHT_PROXY_CONFIG:
                 # This case should already be logged, proxy remains None
                 pass
            # --- End Proxy Setup ---

            print(f"{log_prefix} Launching browser (Headless: {settings.SCRAPER_HEADLESS})...")
            browser = await p.chromium.launch(
                headless=settings.SCRAPER_HEADLESS, # Uses False from ToolSettings instance
                args=browser_args,
                proxy=playwright_proxy # Pass prepared proxy dict or None
            )
            print(f"{log_prefix} Browser launched.")

            context = await browser.new_context( user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36', ignore_https_errors=True, viewport={'width': 1920, 'height': 1080})
            print(f"{log_prefix} Browser context created.")

            if anti_debug_script_content: await context.add_init_script(script=anti_debug_script_content); print(f"{log_prefix} Anti-debugger init script added.")
            else: print(f"{log_prefix} No anti-debug script provided.")

            page = await context.new_page()
            print(f"{log_prefix} New page created.")

            print(f"{log_prefix} Navigating to {target_url}...")
            try:
                await page.goto(target_url, wait_until="domcontentloaded", timeout=90000)
                print(f"{log_prefix} Page loaded. You can now open Developer Tools manually.")
                print(f"{log_prefix} Browser window will remain open...")
                await page.wait_for_event("close", timeout=0)
                print(f"{log_prefix} Page closed event received.")
            except PlaywrightTimeoutError: print(f"{log_prefix} Navigation timed out."); await save_debug_screenshot_pw(page, f"debug_scope_nav_timeout_{int(time.time())}.png", log_prefix)
            except Exception as e: print(f"{log_prefix} Error during navigation/wait: {e}"); await save_debug_screenshot_pw(page, f"debug_scope_error_{int(time.time())}.png", log_prefix)

        except asyncio.CancelledError: print(f"{log_prefix} Script cancelled.")
        except Exception as e: print(f"{log_prefix} Critical setup error: {type(e).__name__} - {e}"); traceback.print_exc(); await save_debug_screenshot_pw(page, f"debug_scope_critical_error_{int(time.time())}.png", log_prefix)
        finally:
            print(f"{log_prefix} Entering cleanup block.")
            if browser and browser.is_connected():
                try: await browser.close(); print(f"{log_prefix} Browser closed.")
                except Exception as close_err: print(f"{log_prefix} Error closing browser: {close_err}")
            else: print(f"{log_prefix} Browser not connected or not initialized.")
            print(f"{log_prefix} Scoping session ended.")

# --- if __name__ == "__main__": block remains the same ---
if __name__ == "__main__":
    # ... (argparse, load JS, find uBlock path) ...
    parser = argparse.ArgumentParser(description="Open a website with Playwright for manual scoping with anti-debug attempts.")
    parser.add_argument("site_alias", choices=TARGET_SITES.keys(), help="Alias of the site to open from the TARGET_SITES dictionary.")
    args = parser.parse_args()
    target_url_to_scope = TARGET_SITES.get(args.site_alias)

    js_content = None
    if os.path.exists(ANTI_DEBUG_JS_FILE_PATH):
        try:
            with open(ANTI_DEBUG_JS_FILE_PATH, 'r', encoding='utf-8') as f: js_content = f.read()
            print(f"[Main] Loaded anti-debug snippets from: {ANTI_DEBUG_JS_FILE_PATH}")
        except Exception as e: print(f"[Main] Error loading anti-debug snippets: {e}")
    else: print(f"[Main] Warning: Anti-debug snippets file not found at {ANTI_DEBUG_JS_FILE_PATH}")

    tool_script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root_for_tool = os.path.dirname(tool_script_dir)
    ublock_base_path_tool = None
    path_option_2_tool = os.path.join(project_root_for_tool, 'extensions', 'ublock_origin_unpacked', 'uBlock-Origin')
    path_option_1_tool = os.path.join(project_root_for_tool, 'extensions', 'ublock_origin_unpacked')
    if os.path.isdir(path_option_2_tool) and os.path.exists(os.path.join(path_option_2_tool, 'manifest.json')): ublock_base_path_tool = path_option_2_tool
    elif os.path.isdir(path_option_1_tool) and os.path.exists(os.path.join(path_option_1_tool, 'manifest.json')): ublock_base_path_tool = path_option_1_tool

    if target_url_to_scope:
        # --- Log the final proxy status decision BEFORE running ---
        print("-" * 30)
        print(f"--- Running Scoping Tool ---")
        print(f"Target Alias: {args.site_alias}")
        print(f"Target URL: {target_url_to_scope}")
        print(f"uBlock Path: {ublock_base_path_tool if ublock_base_path_tool else 'Not Found/Used'}")
        print(f"Anti-Debug Script: {'Loaded' if js_content else 'Not Found/Used'}")
        print(f"Proxy Status: {'ENABLED' if settings.PROXY_ENABLED and settings.PLAYWRIGHT_PROXY_CONFIG else 'DISABLED'}")  #? if statement within a print statement, never seen that one before
        if settings.PROXY_ENABLED and settings.PLAYWRIGHT_PROXY_CONFIG:
             print(f"Proxy Server: {settings.PLAYWRIGHT_PROXY_CONFIG.get('server')}")
        print("-" * 30)
        # --- End Log ---
        asyncio.run(scope_site(target_url_to_scope, ublock_base_path_tool, js_content))
    else: print(f"Error: Invalid site alias '{args.site_alias}' provided.")