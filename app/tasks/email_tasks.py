import logging
from app.core.celery_app import celery_app
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="tasks.send_welcome_email"
)
def send_welcome_email(self, user_email: str, user_name: str) -> dict:
    """
    Send welcome email to new user.

    This task is idempotent and can be safely retried.

    Args:
        user_email: User email address
        user_name: User name

    Returns:
        Result dictionary with status
    """
    try:
        logger.info(f"Sending welcome email to {user_email}")

        email_service = EmailService()

        # Note: Since EmailService methods are async, we need to handle this
        # In a real implementation, you might want to use asyncio.run() or
        # make this task async-compatible
        import asyncio
        result = asyncio.run(
            email_service.send_welcome_email(user_email, user_name)
        )

        if result:
            logger.info(f"Welcome email sent successfully to {user_email}")
            return {
                "status": "success",
                "email": user_email,
                "task_id": self.request.id
            }
        else:
            raise Exception("Email service returned False")

    except Exception as exc:
        logger.error(f"Failed to send welcome email to {user_email}: {exc}")
        # Retry the task
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="tasks.send_password_reset_email"
)
def send_password_reset_email(
    self,
    user_email: str,
    reset_token: str
) -> dict:
    """
    Send password reset email.

    This task is idempotent and can be safely retried.

    Args:
        user_email: User email address
        reset_token: Password reset token

    Returns:
        Result dictionary with status
    """
    try:
        logger.info(f"Sending password reset email to {user_email}")

        email_service = EmailService()

        import asyncio
        result = asyncio.run(
            email_service.send_password_reset_email(user_email, reset_token)
        )

        if result:
            logger.info(
                f"Password reset email sent successfully to {user_email}"
            )
            return {
                "status": "success",
                "email": user_email,
                "task_id": self.request.id
            }
        else:
            raise Exception("Email service returned False")

    except Exception as exc:
        logger.error(
            f"Failed to send password reset email to {user_email}: {exc}"
        )
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    name="tasks.send_notification_email"
)
def send_notification_email(
    self,
    user_email: str,
    subject: str,
    message: str
) -> dict:
    """
    Send generic notification email.

    This task is idempotent and can be safely retried.

    Args:
        user_email: User email address
        subject: Email subject
        message: Email message

    Returns:
        Result dictionary with status
    """
    try:
        logger.info(f"Sending notification email to {user_email}")

        email_service = EmailService()

        import asyncio
        result = asyncio.run(
            email_service.send_email(user_email, subject, message)
        )

        if result:
            logger.info(f"Notification email sent successfully to {user_email}")
            return {
                "status": "success",
                "email": user_email,
                "task_id": self.request.id
            }
        else:
            raise Exception("Email service returned False")

    except Exception as exc:
        logger.error(
            f"Failed to send notification email to {user_email}: {exc}"
        )
        raise self.retry(exc=exc, countdown=60)
