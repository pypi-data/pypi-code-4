"""Admin classes for the ``multilingual_orgs`` app."""
from django.contrib import admin
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

from simple_translation.admin import TranslationAdmin
from simple_translation.utils import get_preferred_translation_from_lang

from .models import Organization


class OrganizationAdmin(TranslationAdmin):
    """Admin for the ``Organization`` model."""
    list_display = ['title', 'phone', 'website']

    def title(self, obj):
        lang = get_language()
        return get_preferred_translation_from_lang(obj, lang).title
    title.short_description = _('Title')


admin.site.register(Organization, OrganizationAdmin)
