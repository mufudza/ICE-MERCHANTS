"""
ASGI config for ice_business project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ice_business.settings')

application = get_asgi_application()