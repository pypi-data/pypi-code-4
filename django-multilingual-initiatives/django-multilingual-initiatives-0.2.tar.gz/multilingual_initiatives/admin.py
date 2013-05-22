"""Admin classes for the ``multilingual_initiatives`` app."""
from django.contrib import admin
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

from django_libs.admin import MultilingualPublishMixin
from simple_translation.admin import TranslationAdmin
from simple_translation.utils import get_preferred_translation_from_lang

from .models import Initiative, InitiativePersonRole


class InitiativePersonRoleInline(admin.TabularInline):
    """Inline admin for ``InitiativePersonRole`` objects."""
    model = InitiativePersonRole


class InitiativeAdmin(MultilingualPublishMixin, TranslationAdmin):
    """Admin for the ``Initiative`` model."""
    inlines = [InitiativePersonRoleInline]
    list_display = ['title', 'phone', 'website', 'start_date', 'end_date',
                    'description_short', 'organization', 'is_published']

    def title(self, obj):
        lang = get_language()
        return get_preferred_translation_from_lang(obj, lang).title
    title.short_description = _('Title')

    def description_short(self, obj):
        if len(obj.description) > 40:
            return obj.description[:40]
        return obj.description
    description_short.short_description = _('Description')


admin.site.register(Initiative, InitiativeAdmin)
