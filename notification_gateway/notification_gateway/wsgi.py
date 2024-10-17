"""
WSGI config for notification_gateway project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

import os
from pathlib import Path
from whitenoise import WhiteNoise
from django.core.wsgi import get_wsgi_application
BASE_DIR = Path(__file__).resolve().parent.parent

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'notification_gateway.settings')

application = get_wsgi_application()
# application = WhiteNoise(application, root=f"/home/appuser/src/notification_gateway/static")