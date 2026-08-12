"""
WSGI config for SkyBound Flight Management System.
Exposes the WSGI callable as a module-level variable named `application`.
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flight_system.settings')
application = get_wsgi_application()
