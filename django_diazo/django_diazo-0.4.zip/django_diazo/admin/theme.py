import os
import zipfile
from codemirror.widgets import CodeMirrorTextarea
from django import forms
from django.contrib import admin
from django.forms import Widget
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
from django_diazo.actions import enable_theme, enable_theme_with_debug, disable_theme
from django_diazo.models import Theme, Rule, ThemeUserAgent


class IFrameWidget(Widget):
    def __init__(self, attrs=None):
        # The 'rows' and 'cols' attributes are required for HTML correctness.
        default_attrs = {'src': 'http://localhost:8000'}
        if attrs:
            default_attrs.update(attrs)
        super(IFrameWidget, self).__init__(default_attrs)

    def render(self, name, value, attrs=None):
        if value is None:
            value = ''
        final_attrs = self.build_attrs(attrs, name=name)
        return mark_safe('<iframe{0} />',
                         forms.util.flatatt(final_attrs))


class ThemeForm(forms.ModelForm):
    upload = forms.FileField(required=False, label=_('Zip file'),
                             help_text=_('Will be unpacked in media directory.'))
    preview = forms.URLField(required=False, widget=IFrameWidget())

    class Meta:
        model = Theme

    def __init__(self, *args, **kwargs):
        super(ThemeForm, self).__init__(*args, **kwargs)

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

        if instance.enabled:
            for t in Theme.objects.all():
                t.enabled = False
                t.save()
        return instance


class UserAgentInline(admin.TabularInline):
    model = ThemeUserAgent
    fields = ['sort', 'pattern', 'allow']
    extra = 1


class ThemeAdmin(admin.ModelAdmin):
    inlines = [UserAgentInline]
    list_display = ('name', 'enabled', 'debug', 'sort',)
    actions = [enable_theme, enable_theme_with_debug, disable_theme]
    form = ThemeForm

    def get_fieldsets(self, request, obj=None):
        """Hook for specifying fieldsets for the different forms."""
        if not obj:
            return (
                (None, {'fields': ('name', 'slug', 'enabled', 'debug', 'sort',)}),
                #(None, {'fields': ('name', 'slug', 'prefix', 'rules', 'enabled', 'debug')}),
                (_('Upload theme'), {'fields': ('upload',)}),
                # (_('Preview'), {'classes': (), 'fields': ('preview',)}),
            )
        elif obj.builtin:
            return (
                (None, {'fields': ('name', 'slug', 'enabled', 'debug', 'sort',)}),
                #(_('Built-in settings'), {'classes': ('collapse',), 'fields': ('path', 'url', 'builtin',)})
                # (_('Preview'), {'classes': (), 'fields': ('preview',)}),
            )
        else:
            return (
                (None, {'fields': ('name', 'slug', 'enabled', 'debug', 'sort',)}),
                #(None, {'fields': ('name', 'slug', 'prefix', 'rules', 'enabled', 'debug')}),
                # (_('Preview'), {'classes': (), 'fields': ('preview',)}),
            )

    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        if db_field.name == 'rules':
            kwargs['queryset'] = Rule.objects.filter(root=True)
            return db_field.formfield(**kwargs)
        return super(ThemeAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(Theme, ThemeAdmin)
