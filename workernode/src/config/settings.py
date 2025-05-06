# src/config/settings.py
import os
from dotenv import load_dotenv

# Load variables from .env file into environment
load_dotenv()

# Redis/Celery Config
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SCRAPE_QUEUE_NAME = os.getenv("SCRAPE_QUEUE_NAME", "media-scrape-jobs")

# Worker Config
WORKER_CONCURRENCY = int(os.getenv("WORKER_CONCURRENCY", "1"))

# Scraper Config
SCRAPER_HEADLESS = os.getenv("HEADLESS_MODE", "True")
SCRAPER_TIMEOUT_SECONDS = int(os.getenv("BROWSER_TIMEOUT", "120"))

# Proxy Config (read only if enabled)
PROXY_ENABLED = os.getenv("PROXY_ENABLED", "False")
PROXY_CONFIG = None
if PROXY_ENABLED:
    user = os.getenv("PROXY_USER")
    password = os.getenv("PROXY_PASS")
    host = os.getenv("PROXY_HOST")
    port = os.getenv("PROXY_PORT")
    proxy_type = os.getenv("PROXY_TYPE") 

    if user and password and host and port:
        proxy_url = f"{proxy_type}://{user}:{password}@{host}:{port}"
        PROXY_CONFIG = {
            'proxy': {
                'http': proxy_url,
                'https': proxy_url,
                'no_proxy': 'localhost,127.0.0.1' # Important
            }
            # Add 'auth': (user, password) here if selenium-wire needs it separately
        }
        print(f"Proxy configured: Type={proxy_type}, Host={host}") # Don't log user/pass
    else:
        print("Warning: PROXY_ENABLED is True but some proxy details are missing in .env")
        PROXY_ENABLED = False # Disable if details missing

# Validate mandatory settings
if not REDIS_URL or not SCRAPE_QUEUE_NAME:
    raise ValueError("REDIS_URL and SCRAPE_QUEUE_NAME must be set in .env")

print(f"--- Worker Configuration ---")
print(f"Redis URL: {REDIS_URL}")
print(f"Scrape Queue Name: {SCRAPE_QUEUE_NAME}")
print(f"Concurrency: {WORKER_CONCURRENCY}")
print(f"Scraper Headless: {SCRAPER_HEADLESS}")
print(f"Scraper Timeout (s): {SCRAPER_TIMEOUT_SECONDS}")
print(f"Proxy Enabled: {PROXY_ENABLED}")
print(f"--------------------------")







