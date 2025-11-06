"""
Celery worker startup script.

Run this script to start the Celery worker:
    celery -A worker.start:celery_app worker --loglevel=info
"""

import logging
from app.core.celery_app import celery_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # Start the worker
    celery_app.worker_main([
        "worker",
        "--loglevel=info",
        "--concurrency=4",
        "--max-tasks-per-child=1000"
    ])
