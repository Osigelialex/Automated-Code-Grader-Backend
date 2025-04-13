"""
WSGI config for checkmate project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from decouple import config

if config('DEBUG') == 'True':
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkmate.settings.development')
else:
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'checkmate.settings.production')

application = get_wsgi_application()

app = application