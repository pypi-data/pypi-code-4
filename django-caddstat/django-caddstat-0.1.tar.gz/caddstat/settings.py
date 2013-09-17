"""
Set default django setting values for CADD Stat
"""

from django.conf import settings


CADDSTAT_FEEDBACK_EMAIL = getattr(settings, 'CADDSTAT_FEEDBACK_EMAIL', 'test@example.com')