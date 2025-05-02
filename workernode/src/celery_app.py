# src/celery_app.py
from celery import Celery
from src.config import settings # Import our centralized settings

# Initialize Celery
# The first argument is the "main module name" - usually the project folder name
# The broker is the Redis URL
# The backend is also Redis here, used to store task results (optional but useful)
celery_app = Celery(
    'worker_node_py',
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL, # Use redis for results too
    include=['src.tasks.scrape_tasks'] # Tell Celery where to find tasks
)

# Optional Celery configuration
celery_app.conf.update(
    task_serializer='json',       # Use JSON for task messages
    accept_content=['json'],      # Accept JSON content
    result_serializer='json',     # Store results as JSON
    timezone='UTC',               # Use UTC timezone
    enable_utc=True,
    # Set a default task timeout slightly less than the scraper timeout
    task_time_limit=settings.SCRAPER_TIMEOUT_SECONDS - 10,
    task_soft_time_limit=settings.SCRAPER_TIMEOUT_SECONDS - 20,
)

if __name__ == '__main__':
    # Allows starting worker via 'python -m src.celery_app worker ...' if needed
    celery_app.start()