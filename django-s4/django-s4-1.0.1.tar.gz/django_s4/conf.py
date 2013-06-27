from django.conf import settings

DRIVE_UPLOAD_URL = getattr(settings, "S4_DRIVE_UPLOAD_URL", "http://127.0.0.1:8484/")
DRIVE_STATIC_URL = getattr(settings, "S4_DRIVE_STATIC_URL", "")