"""Registering translated models for the ``multilingual_orgs`` app."""
from simple_translation.translation_pool import translation_pool

from .models import Organization, OrganizationTranslation


translation_pool.register_translation(Organization, OrganizationTranslation)
