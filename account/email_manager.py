from django.template.loader import render_to_string
from django.utils.crypto import get_random_string
from django.core.mail import EmailMessage
from django.db import transaction
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
    
    def generate_user_token(self, user, expiry: Optional[timezone.timedelta] = None) -> str:
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
            cache.set(token, user.id, timeout=(expiry or self.token_expiry).seconds)
            return token
        except Exception as e:
            logger.error(f"Token generation failed for user {user.id}: {str(e)}")
            raise
    
    def send_email(
        self,
        template_path: str,
        context: Dict[str, Any],
        subject: str,
        to_email: str
    ) -> None:
        """
        Send an HTML email using a template.
        
        Args:
            template_path: Path to the email template
            context: Template context dictionary
            subject: Email subject
            to_email: Recipient email address
            
        Raises:
            TemplateDoesNotExist: If template is not found
            SMTPException: If email sending fails
        """
        try:
            email_body = render_to_string(template_path, context)
            email = EmailMessage(
                subject=subject,
                body=email_body,
                from_email=self.from_email,
                to=[to_email]
            )
            email.content_subtype = 'html'
            email.send(fail_silently=False)
            logger.info(f"Email sent successfully to {to_email}")
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise

    @transaction.atomic
    def send_activation_email(self, user) -> None:
        """
        Send account activation email to user.
        
        Args:
            user: User object to send activation email to
            
        Raises:
            Exception: If email sending fails
        """
        try:
            token = self.generate_user_token(user)
            confirmation_url = (
                f'{self.env("CLIENT_URL")}/verify-token'
                f'?token={token}'
            )
            
            context = {
                'user': user,
                'confirmation_url': confirmation_url,
                'year': timezone.now().year
            }
            
            self.send_email(
                template_path='email_confirmation.html',
                context=context,
                subject='Activate Your Checkmate Account',
                to_email=user.email
            )

            logger.info(f'Confirmation url: {confirmation_url}')
        except Exception as e:
            logger.error(f"Activation email failed for user {user.id}: {str(e)}")
            raise

    @transaction.atomic
    def send_password_reset_email(self, user) -> None:
        """
        Send password reset email to user.
        
        Args:
            user: User object to send password reset email to
            
        Raises:
            Exception: If email sending fails
        """
        try:
            token = self.generate_user_token(
                user,
                expiry=timezone.timedelta(hours=1)
            )
            password_reset_url = (
                f'{self.env("CLIENT_URL")}/api/v1/auth/reset_password'
                f'?token={token}'
            )
            
            context = {
                'user': user,
                'password_reset_url': password_reset_url,
                'year': timezone.now().year
            }
            
            self.send_email(
                template_path='password_reset.html',
                context=context,
                subject='Reset your Checkmate password',
                to_email=user.email
            )

            logger.info(f'Password reset url: {password_reset_url}')

        except Exception as e:
            logger.error(f"Password reset email failed for user {user.id}: {str(e)}")
            raise

email_manager = EmailManager()