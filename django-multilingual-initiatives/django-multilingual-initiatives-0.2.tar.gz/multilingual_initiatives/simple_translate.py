"""Registering translated models for the ``multilingual_initiatives`` app."""
from simple_translation.translation_pool import translation_pool

from .models import Initiative, InitiativeTranslation


translation_pool.register_translation(Initiative, InitiativeTranslation)
