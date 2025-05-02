# send_test_job.py
from src.tasks.scrape_tasks import process_scrape_request # Import the TASK
from src.config import settings # To ensure env loaded if run directly
import uuid

# !!! REPLACE WITH A VALID URL FROM YOUR MIRROR SITE !!!
test_url = "https://ww19.0123movie.net/home.html"
test_id = f"test_movie_{uuid.uuid4()}" # Unique ID for testing
test_type = "movie"

if __name__ == "__main__":
    if not test_url or "your-mirror-site.com" in test_url:
        print("!!! Please replace 'test_url' in send_test_job.py with a real target URL !!!")
    else:
        print(f"Sending test job for URL: {test_url}")
        job_data = {
            'targetUrl': test_url,
            'mediaId': test_id,
            'mediaType': test_type
        }
        # Use .delay() to send the job to the queue
        process_scrape_request.delay(job_data)
        print(f"Job sent to queue '{settings.SCRAPE_QUEUE_NAME}' with ID {test_id}.")
        

#? The send_test_job.py script's only job is to put a message onto the Redis queue. It does not configure the Celery worker process.