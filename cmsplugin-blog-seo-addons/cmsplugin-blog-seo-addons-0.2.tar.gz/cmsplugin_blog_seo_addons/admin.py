"""Admin classes for the ``entry_seo_addons`` app."""
from django.contrib import admin
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

from cmsplugin_blog.admin import EntryAdmin
from simple_translation.admin import TranslationAdmin
from simple_translation.utils import get_preferred_translation_from_lang

from .models import SEOAddon, EntrySEOAddon


class SEOAddonAdmin(TranslationAdmin):
    """Admin class for the ``SEOAddon`` model."""
    list_display = ['meta_description', 'languages']

    def meta_description(self, obj):
        lang = get_language()
        return get_preferred_translation_from_lang(obj, lang).meta_description
    meta_description.short_description = _('Meta description')


class SEOAddonInline(admin.TabularInline):
    model = EntrySEOAddon
    max_num = 1


EntryAdmin.inlines = EntryAdmin.inlines[:] + [SEOAddonInline]


admin.site.register(SEOAddon, SEOAddonAdmin)
