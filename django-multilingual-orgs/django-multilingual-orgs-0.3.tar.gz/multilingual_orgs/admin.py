"""Admin classes for the ``multilingual_orgs`` app."""
from django.contrib import admin
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

from django_libs.admin import MultilingualPublishMixin
from simple_translation.admin import TranslationAdmin
from simple_translation.utils import get_preferred_translation_from_lang

from .models import Organization, OrganizationPersonRole


class OrganizationPersonRoleInline(admin.TabularInline):
    """Inline admin for ``OrganizationPersonRole`` objects."""
    model = OrganizationPersonRole


class OrganizationAdmin(MultilingualPublishMixin, TranslationAdmin):
    """Admin for the ``Organization`` model."""
    inlines = [OrganizationPersonRoleInline]
    list_display = ['title', 'phone', 'website', 'is_published']

    def title(self, obj):
        lang = get_language()
        return get_preferred_translation_from_lang(obj, lang).title
    title.short_description = _('Title')


admin.site.register(Organization, OrganizationAdmin)
