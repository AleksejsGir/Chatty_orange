"""
Settings router for Chatty_orange project.
"""

import os

# Determine which settings to use based on environment variable
if os.environ.get('DJANGO_SETTINGS_MODULE') == 'Chatty_orange.settings.production':
    from .production import *
else:
    from .development import *