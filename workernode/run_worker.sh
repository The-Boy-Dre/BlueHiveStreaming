#!/bin/bash

# Get the directory where the script resides
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Activate virtual environment if you are using one
# echo "Activating virtual environment..."
# source "$DIR/venv/bin/activate" # Adjust path to your venv if needed

echo "Starting Celery worker..."

# Change to the worker directory before running celery
cd "$DIR"

# Start celery worker
# -A points to the celery app instance (src folder -> celery_app module -> celery_app variable)
# -l sets the log level
# -c sets the concurrency (number of worker processes) - read from env
celery -A src.celery_app worker --loglevel=INFO -c ${WORKER_CONCURRENCY:-1}

echo "Celery worker stopped."

# Deactivate virtual environment if used
# deactivate