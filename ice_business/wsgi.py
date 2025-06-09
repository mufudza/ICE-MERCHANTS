"""
WSGI config for ice_business project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ice_business.settings')

application = get_wsgi_application()