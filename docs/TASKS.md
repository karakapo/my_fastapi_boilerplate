# Background Tasks Guide

## Task Types

### 1. Immediate Async
- **Purpose**: Operations that should run immediately but not block the response
- **Examples**: Email notifications, webhooks
- **Usage**: `task.delay(args)`

### 2. Scheduled Tasks
- **Purpose**: Recurring operations on a schedule
- **Examples**: Daily reports, data cleanup, cache warming
- **Usage**: Celery beat scheduler

### 3. Heavy Processing
- **Purpose**: CPU/time-intensive operations
- **Examples**: Data analysis, file processing, report generation
- **Usage**: `task.apply_async(args, time_limit=600)`

## Task Best Practices

### 1. Keep Tasks Idempotent
Tasks should produce the same result when called multiple times with same input.

```python
# Good - idempotent
@celery_app.task
def send_welcome_email(user_id: str):
    # Check if email already sent
    if email_already_sent(user_id):
        return
    send_email(user_id)
    mark_email_sent(user_id)

# Bad - not idempotent
@celery_app.task
def increment_counter(user_id: str):
    counter = get_counter(user_id)
    set_counter(user_id, counter + 1)  # Running twice = wrong count
```

### 2. Add Retry Logic
Always add retry logic for tasks that might fail due to transient issues.

```python
@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_email(self, user_email: str):
    try:
        email_service.send(user_email)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

### 3. Log Errors Properly
Use structured logging for better debugging.

```python
import logging
logger = logging.getLogger(__name__)

@celery_app.task
def process_data(user_id: str):
    try:
        logger.info(f"Processing data for user {user_id}")
        # ... processing ...
        logger.info(f"Completed processing for user {user_id}")
    except Exception as e:
        logger.error(f"Failed to process data for user {user_id}: {e}")
        raise
```

### 4. Don't Pass Large Objects
Pass IDs instead of full objects to keep task payload small.

```python
# Good
@celery_app.task
def process_user(user_id: str):
    user = db.get_user(user_id)
    # ... process ...

# Bad
@celery_app.task
def process_user(user_dict: dict):  # Large payload
    # ... process ...
```

### 5. Set Timeout
Always set time limits to prevent tasks from running forever.

```python
@celery_app.task(
    time_limit=600,      # Hard limit: 10 minutes
    soft_time_limit=540  # Soft limit: 9 minutes
)
def heavy_processing(data_id: str):
    # ... processing ...
```

## Creating a New Task

### Step 1: Define the Task
Create task in `app/tasks/` directory:

```python
# app/tasks/my_tasks.py
from app.core.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)

@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="tasks.my_custom_task"
)
def my_custom_task(self, arg1: str, arg2: int) -> dict:
    """
    Task description.

    Args:
        arg1: Description
        arg2: Description

    Returns:
        Result dictionary
    """
    try:
        logger.info(f"Starting task with {arg1}, {arg2}")

        # Task logic here
        result = {"status": "success", "data": "..."}

        logger.info("Task completed successfully")
        return result

    except Exception as exc:
        logger.error(f"Task failed: {exc}")
        raise self.retry(exc=exc, countdown=60)
```

### Step 2: Register Task
Add to `app/core/celery_app.py`:

```python
celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.data_processing_tasks",
        "app.tasks.my_tasks"  # Add your tasks module
    ]
)
```

### Step 3: Call the Task
From your API route or service:

```python
from app.tasks.my_tasks import my_custom_task

# Fire and forget
my_custom_task.delay("arg1", 123)

# Get result later
result = my_custom_task.apply_async(
    args=["arg1", 123],
    countdown=60  # Run after 60 seconds
)
task_id = result.id
```

## Monitoring Tasks

### Check Task Status
```python
from celery.result import AsyncResult

result = AsyncResult(task_id, app=celery_app)
print(result.state)  # PENDING, STARTED, SUCCESS, FAILURE
print(result.result)  # Task return value
```

### Monitor Queue Length
```bash
celery -A app.core.celery_app:celery_app inspect active
celery -A app.core.celery_app:celery_app inspect scheduled
celery -A app.core.celery_app:celery_app inspect reserved
```

## Scheduled Tasks with Celery Beat

Add to `app/core/celery_app.py`:

```python
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'cleanup-every-day': {
        'task': 'tasks.cleanup_old_data',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM
    },
    'send-reports-weekly': {
        'task': 'tasks.generate_weekly_report',
        'schedule': crontab(day_of_week=1, hour=9),  # Monday 9 AM
    },
}
```

Start beat scheduler:
```bash
celery -A app.core.celery_app:celery_app beat --loglevel=info
```

## Common Task Patterns

### Email Task
```python
@celery_app.task(bind=True, max_retries=3)
def send_email(self, to: str, subject: str, body: str):
    try:
        email_service.send(to, subject, body)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
```

### Batch Processing
```python
@celery_app.task
def process_batch(item_ids: list):
    for item_id in item_ids:
        process_item.delay(item_id)
```

### Chain Tasks
```python
from celery import chain

# Run tasks sequentially
result = chain(
    task1.s(arg1),
    task2.s(),
    task3.s()
)()
```

### Group Tasks
```python
from celery import group

# Run tasks in parallel
job = group([
    task.s(i) for i in range(10)
])
result = job.apply_async()
```
