"""Registering translated models for the ``cmsplugin_blog_seo_addons`` app."""
from simple_translation.translation_pool import translation_pool

from .models import SEOAddon, SEOAddonTranslation


translation_pool.register_translation(SEOAddon, SEOAddonTranslation)
