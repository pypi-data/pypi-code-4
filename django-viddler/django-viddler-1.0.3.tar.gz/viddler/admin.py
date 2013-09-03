# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.admin import helpers
from django.core.urlresolvers import reverse
from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.encoding import force_text
from .forms import ViddlerUploadForm
from .settings import get_viddler


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = [super(AdminImageWidget, self).render(name, value, attrs), '<p class="file-upload">']
        if value and hasattr(value, 'instance') and value.instance.thumbnail:
            thumbnail = value.instance.thumbnail.url
            width = value.instance.thumb_width
            height = value.instance.thumb_height
            tag = u'<img src="%s" width="%s" height="%s"/>' % (
                thumbnail, width, height)
        else:
            tag = _("<strong>No Thumbnail available</strong>")
        if value:
            output.append(u'<a href="%s" target="_blank">%s</a>' % (
                value.url, tag))
        output.append('</p>')
        return mark_safe(u''.join(output))


class ViddlerAdmin(admin.ModelAdmin):
    add_form_template = "admin/viddler/viddlervideo/add_form.html"

    add_form = ViddlerUploadForm

    readonly_fields = ('viddler_id', 'last_synced', 'status', 'author', 'length',
        'url', 'thumbnail_url', 'html5_video_source', 'audio_only', 'view_count',
        'impression_count', 'upload_time', 'made_public_time', 'favorite',
        'comment_count', 'thumbnails_count', 'thumbnail_index', 'files')

    add_fieldsets = (
        (None, ({
            'fields': ('uploadtoken', 'callback', 'title', 'description', 'slug', 'file')
        })),
    )

    change_fieldsets = (
        (None, {
            'fields': ('viddler_id', 'status', 'author', 'last_synced')
        }),
        ('Details', {
            'fields': ('title', 'description', 'tags', 'permalink',
                'age_limit', 'length', 'url', 'html5_video_source',
                'thumbnail_url', ),
        }),
        ('Interaction', {
            'fields': ('view_permission', 'embed_permission',
                'tagging_permission', 'commenting_permission',
                'download_permission', ),
        }),
        ('Counts', {
            'fields': ('view_count', 'impression_count', 'favorite',
            'comment_count', 'upload_time', 'made_public_time', ),
        }),
    )
    prepopulated_fields = {"slug": ("title",)}

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'key_image_custom':
            kwargs['widget'] = AdminImageWidget
            kwargs.pop('request')
            return db_field.formfield(**kwargs)
        return super(ViddlerAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def get_fieldsets(self, request, obj=None):
        if obj:
            return self.change_fieldsets
        else:
            return self.add_fieldsets

    def sync_url(self):
        return reverse("viddler_callback", kwargs={'videoid': self.model.viddler_id})

    def add_view(self, request, form_url='', extra_context=None):
        model = self.model
        opts = model._meta
        formsets = []
        inline_admin_formsets = []
        viddler = get_viddler()
        info = viddler.videos.prepareUpload()
        callback_url = "http://%s%s" % (request.get_host(), reverse('viddler_callback'))
        form = self.add_form(initial={
            'uploadtoken': info['token'],
            'callback': callback_url
        })
        fieldsets = self.add_fieldsets
        adminForm = helpers.AdminForm(form, fieldsets,
            self.get_prepopulated_fields(request),
            self.get_readonly_fields(request),
            model_admin=self)

        media = self.media + adminForm.media

        context = {
            'title': 'Add %s' % force_text(opts.verbose_name),
            'adminform': adminForm,
            'is_popup': "_popup" in request.REQUEST,
            'media': media,
            'inline_admin_formsets': inline_admin_formsets,
            'errors': helpers.AdminErrorList(form, formsets),
            'app_label': opts.app_label,
            'show_delete': False,
            'uploadtoken': info['token'],
            'endpoint': info['endpoint'],
            'callback': callback_url
        }
        context.update(info)
        context.update(extra_context or {})
        return self.render_change_form(request, context, add=True, form_url=info['endpoint'])

from django.conf import settings
if 'viddler' in settings.INSTALLED_APPS:
    from .models import ViddlerVideo
    admin.site.register(ViddlerVideo, ViddlerAdmin)
