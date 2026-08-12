"""
ASGI config for SkyBound Flight Management System.
Exposes the ASGI callable as a module-level variable named `application`.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flight_system.settings')
application = get_asgi_application()
