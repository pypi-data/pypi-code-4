import os
import zipfile
from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django_diazo.actions import enable_theme, enable_theme_with_debug, disable_theme
from django_diazo.models import Theme, Rule, ThemeUserAgent


class ThemeForm(forms.ModelForm):
    upload = forms.FileField(required=False, label=_('Zip file'),
                             help_text=_('Will be unpacked in media directory.'))

    class Meta:
        model = Theme

    def save(self, commit=True):
        instance = super(ThemeForm, self).save(commit)
        instance.save()  # We need the pk

        if 'upload' in self.files:
            f = self.files['upload']
            z = zipfile.ZipFile(f)
            z.extractall(instance.theme_path(False))

        path = instance.theme_path()
        if not os.path.exists(path):
            os.makedirs(path)

        return instance


class UserAgentInline(admin.TabularInline):
    model = ThemeUserAgent
    fields = ['sort', 'pattern', 'allow']
    extra = 1


class ThemeAdmin(admin.ModelAdmin):
    inlines = [UserAgentInline]
    list_display = ('name', 'enabled', 'debug', 'sort', 'theme_url', 'theme_path',)
    list_editable = ('enabled', 'debug',)
    exclude = ('builtin', 'url', 'path',)
    list_filter = ('enabled', 'debug',)
    actions = [enable_theme, enable_theme_with_debug, disable_theme]
    form = ThemeForm

    def get_fieldsets(self, request, obj=None):
        """Hook for specifying fieldsets for the different forms."""
        if not obj:
            return (
                (None, {'fields': ('name', 'slug', 'enabled', 'debug', 'sort', 'prefix',)}),
                (_('Upload theme'), {'fields': ('upload',)}),
            )
        elif obj.builtin:
            return (
                (None, {'fields': ('name', 'slug', 'enabled', 'debug', 'sort', 'prefix',)}),
            )

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'rules':
            kwargs['queryset'] = Rule.objects.filter(root=True)
            return db_field.formfield(**kwargs)
        return super(ThemeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Theme, ThemeAdmin)
