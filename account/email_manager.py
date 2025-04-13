from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.core.mail import EmailMultiAlternatives, get_connection
from django.db import transaction
from django.utils.html import strip_tags
from django.utils import timezone
from django.conf import settings
from django.core.cache import cache
from typing import Any, Dict, Optional
import environ, logging

logger = logging.getLogger(__name__)


class EmailManager:
    """
    Handles email operations including token generation, email rendering and sending.
    
    This class provides a centralized way to manage all email-related functionality
    including activation emails and password reset emails.
    """

    def __init__(self):
        self.env = environ.Env()
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.token_expiry = timezone.timedelta(minutes=15)
    
    def generate_user_token(self, user_id: str, expiry: Optional[timezone.timedelta] = None) -> str:
        """
        Generate a secure token for user verification purposes.
        
        Args:
            user: The user object to generate token for
            expiry: Optional custom expiration time delta
            
        Returns:
            str: Generated token
        """
        try:
            token = get_random_string(length=64)
            cache.set(token, user_id, timeout=(expiry or self.token_expiry).seconds)
            return token
        except Exception as e:
            logger.error(f"Token generation failed for user {user_id}: {str(e)}")
            raise
    
    def send_email(subject, recipient, context, template_name):
        """
        Utility to send an email with HTML and plain text content.

        Args:
            subject: Email subject
            recipient: Recipient email address
            context: Context for the email template
            template_name: Path to the email template
        """
        try:
            html_message = render_to_string(template_name, context)
            plain_message = strip_tags(html_message)
    
            with get_connection() as connection:
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient],
                    connection=connection,
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
        except Exception as e:
            logger.error(f"Error sending email to {recipient}: {e}")
            raise

    @transaction.atomic
    def send_activation_email(self, user_id: str, first_name: str, email: str) -> None:
        """
        Send account activation email to user.
        
        Args:
            user: User object to send activation email to
            
        Raises:
            Exception: If email sending fails
        """
        try:
            token = self.generate_user_token(user_id)
            confirmation_url = (
                f'{self.env("CLIENT_URL")}/verify-token'
                f'?token={token}'
            )
            
            context = {
                'first_name': first_name,
                'confirmation_url': confirmation_url,
                'year': timezone.now().year
            }
            
            self.send_email(
                subject='Activate Your Checkmate Account',
                recipient=email,
                context=context,
                template_name='email_confirmation.html'
            )

            logger.info(f'Confirmation url: {confirmation_url}')
        except Exception as e:
            logger.error(f"Activation email failed for user {user_id}: {str(e)}")
            raise

    @transaction.atomic
    def send_password_reset_email(self, user_id: str, first_name: str, email: str) -> None:
        """
        Send password reset email to user.

        Args:
            user: User object to send password reset email to
            
        Raises:
            Exception: If email sending fails
        """
        try:
            token = self.generate_user_token(
                user_id,
                expiry=timezone.timedelta(hours=1)
            )
            password_reset_url = (
                f'{self.env("CLIENT_URL")}/change-password'
                f'?token={token}'
            )
            
            context = {
                'first_name': first_name,
                'password_reset_url': password_reset_url,
                'year': timezone.now().year
            }
            
            self.send_email(
                subject='password_reset.html',
                recipient=email,
                context=context,
                template_name='password_reset.html'
            )

            logger.info(f'Password reset url: {password_reset_url}')

        except Exception as e:
            logger.error(f"Password reset email failed for user {user_id}: {str(e)}")
            raise

email_manager = EmailManager()