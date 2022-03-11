"""
WSGI config for LuojiaWaf project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import logging

from django.core.wsgi import get_wsgi_application
from common import log_utils

log_utils.custom_init(level=logging.WARNING)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LuojiaWaf.settings')

application = get_wsgi_application()
