"""Admin classes for the ``cmsplugin_blog_language_publish`` app."""
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

from cmsplugin_blog.models import Entry
from cmsplugin_blog.admin import EntryAdmin, EntryForm

from simple_translation.translation_pool import translation_pool
from simple_translation.utils import get_preferred_translation_from_lang

from .models import EntryLanguagePublish


class EntryLanguagePublishAdmin(admin.ModelAdmin):
    """
    Admin for the ``EntryLanguagePublish`` model.

    Mainly used for debugging purposes. You would rather set the publish
    flag when editing a blog entry via the EntryAdmin.

    """
    list_display = (
        'title', 'language', 'is_published')

    def title(self, obj):
        return obj.entry_title.title

    def language(self, obj):
        return obj.entry_title.language


class CustomEntryForm(EntryForm):
    """
    Custom form for the ``Entry`` model, used by the ``EntryAdmin``.

    This is quite a hack. We will always set the `is_published` of the Entry
    model to true and we will override the initial value for the `is_published`
    field with the corresponding value of a ``EntryLanguagePublish`` object.

    """
    def __init__(self, *args, **kwargs):
        super(CustomEntryForm, self).__init__(*args, **kwargs)

        model = self._meta.model
        info = translation_pool.get_info(model)
        self.current_language = self.base_fields[info.language_field].initial
        title = None
        if self.instance and self.instance.pk:
            try:
                title = self.instance.entrytitle_set.get(
                    language=self.current_language)
            except ObjectDoesNotExist:
                pass

        publish = None
        if title:
            try:
                publish = EntryLanguagePublish.objects.get(
                    entry_title=title)
            except EntryLanguagePublish.DoesNotExist:
                pass

        self.initial['is_published'] = (
            publish and publish.is_published or False)

    def save(self, *args, **kwargs):
        """
        Setting ``is_published`` of the ``Entry`` always to ``True``.

        Since we no longer use this field in the admin, we will just always
        set it to true.

        """
        self.instance.is_published = True
        return super(CustomEntryForm, self).save(*args, **kwargs)


class CustomEntryAdmin(EntryAdmin):
    """
    Custom admin for the ``Entry`` model.

    """
    form = CustomEntryForm
    list_display = ('title', 'languages', 'author', 'pub_date',
                    'is_published_lang')
    list_editable = ()
    list_filter = ('pub_date', )

    def title(self, obj):
        lang = get_language()
        return get_preferred_translation_from_lang(obj, lang).title

    def is_published_lang(self, obj):
        """
        This is a copy from the ``is_pubished`` method of the
        ``MultilingualPublishMixin``. Only providing the mixin and adding
        ``is_published`` would have resulted in adding the entry's field to the
        list instead of using the mixin version.

        """
        languages = ''
        for trans in obj.translations:
            if trans.is_published:
                if languages == '':
                    languages = trans.language
                else:
                    languages += ', {0}'.format(trans.language)
        if languages == '':
            return _('Not published')
        return languages
    is_published_lang.short_description = _('Is published')

    def save_model(self, request, obj, form, change):
        """
        Creating the ``EntryLanguagePublish`` model after saving the ``Entry``.

        Unfortunately this can't be done in the form's ``save()`` method. The
        admin only creates the ``EntryTitle`` object in this method. Therefore
        we override it and create our ``EntryLanguagePublish`` model here.

        """
        super(CustomEntryAdmin, self).save_model(request, obj, form, change)
        title = obj.entrytitle_set.get(language=form.current_language)
        published, created = EntryLanguagePublish.objects.get_or_create(
            entry_title=title)
        published.is_published = form.cleaned_data.get('is_published')
        published.save()


admin.site.unregister(Entry)
admin.site.register(Entry, CustomEntryAdmin)
admin.site.register(EntryLanguagePublish, EntryLanguagePublishAdmin)
