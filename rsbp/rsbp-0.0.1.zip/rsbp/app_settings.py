from django.conf import settings

RSBP_IMAGE_UPLOAD_DIR = getattr(settings, 'IMAGE_UPLOAD_DIR', 'uploads')
RSBP_POSTS_PER_PAGE = getattr(settings, 'POSTS_PER_PAGE', 5)
RSBP_FEED_TITLE = getattr(settings, 'RSBP_FEED_TITLE', 'Blog')
RSBP_FEED_LINK = getattr(settings, 'RSBP_FEED_LINK', '/')
RSBP_FEED_DESCRIPTION = getattr(settings, 'RSBP_FEED_DESCRIPTION', '')
RSBP_FEED_MAX_ITEMS = getattr(settings, 'RSBP_MAX_FEED_MAX_ITEMS', 10)
