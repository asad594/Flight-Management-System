"""
SkyBound Core Application Configuration.
Declares Django application registry settings and metadata for the core domain module.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration class for SkyBound core flight management application."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    verbose_name = 'SkyBound Flight Management'

