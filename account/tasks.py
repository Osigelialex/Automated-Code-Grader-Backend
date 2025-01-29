from celery import shared_task
from account.email_manager import EmailManager


@shared_task(bind=True, max_retries=3, default_retry_delay=20)
def send_activation_email(self, user_id: str, first_name: str, email: str):
    """
    Send activation email to user.
    
    Args:
        user: User object to send activation email to
    """
    email_manager = EmailManager()
    email_manager.send_activation_email(user_id, first_name, email)


@shared_task(bind=True, max_retries=3, default_retry_delay=20)
def send_password_reset_email(self, user_id: str, first_name: str, email: str):
    """
    Send password reset email to user.
    
    Args:
        user: User object to send password reset email to
    """
    email_manager = EmailManager()
    email_manager.send_password_reset_email(user_id, first_name, email)
