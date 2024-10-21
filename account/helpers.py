from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.utils import timezone
from .models import Token
import base64
import environ


def send_activation_email(user):
    env = environ.Env()
    uid = base64.b64encode(str(user.pk).encode()).decode('utf-8')

    token = account_activation_token.make_token(user)
    Token.objects.create(
        user=user,
        key=token,
        expires_at=timezone.now() + timezone.timedelta(minutes=15)
    )

    confimation_url = f'{env('BASE_URL')}/api/v1/account/activate/?uid={uid}&token={token}/'

    subject = 'Activate Your Account - Codegradr'
    email_body = render_to_string('email_confirmation.html', {
        'user': user,
        'confimation_url': confimation_url,
        'year': timezone.now()
    })

    email = EmailMessage(
        subject=subject,
        body=email_body,
        from_email='noreply@codegradr.com',
        to=[user.email]
    )

    email.content_subtype = 'html'
    email.send()

    print(f'{confimation_url}')