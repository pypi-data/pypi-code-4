from django.contrib import admin
from django.conf.urls import patterns, url
from django.contrib.admin import helpers
from django.contrib.admin.util import unquote
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse
from django.template.response import TemplateResponse

from dprofiling.forms import StatsForm
from dprofiling.models import Session, Profile
from dprofiling.backends import get_backend





class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'path', 'active', 'stats_link')
    list_filter = ('active',)

    def stats_link(self, obj):
        return '<a href="%s">Stats</a>' % (reverse('admin:dprofiling_session_stats',
            args=(obj.pk,)),)

    stats_link.allow_tags = True
    stats_link.short_description = 'Cumulative Stats'

    def get_urls(self):
        urls = super(SessionAdmin, self).get_urls()
        info = (self.model._meta.app_label,
                        self.model._meta.module_name)
        session_urls = patterns('',
                url(r'^(.+)/stats/$',
                    self.admin_site.admin_view(self.stats_view),
                    name='%s_%s_stats' % info),
            )
        return session_urls + urls

    def stats_view(self, request, object_id, extra_context=None):
        """ Render a view for selecting details before printing stats """
        opts = self.model._meta
        app_label = opts.app_label
        backend = get_backend()
        if not callable(getattr(backend, 'get_stats', None)):
            raise Exception('Current backend does not support getting '
                    'aggregate stats')
        obj = self.get_object(request, unquote(object_id))

        if obj is None:
            raise Http404('Stats object does not exist')

        if request.method == 'POST':
            form = StatsForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                stats, output = backend.get_stats(obj)
                if not stats:
                    raise Http404('No stats collected for this object')
                if data['strip_dirs']:
                    stats.strip_dirs()
                if data['sort']:
                    stats.sort_stats(*data['sort'])
                if data['reverse_sort']:
                    stats.reverse_order()
                method = getattr(stats, 'print_%s' % (data['method'],))
                method(*data['restrictions'])
                return HttpResponse(output.getvalue(),
                    content_type='text/plain')
        else:
            form = StatsForm()

        adminform = helpers.AdminForm(form,
                [
                    (None, {'fields':[
                        'sort','reverse_sort','strip_dirs', 'restrictions','method']
                        }),
                ], {})

        context = {
            'title': 'Stats for %s' % obj.name,
            'adminform': adminform,
            'object_id': object_id,
            'original': obj,
            'is_popup': "_popup" in request.REQUEST,
            'errors': helpers.AdminErrorList(form, None),
            'app_label': opts.app_label,
            'opts': opts,
            'add': False,
        }
        context.update(extra_context or {})
        return TemplateResponse(request,
                ['admin/dprofiling/session/stats_form.html'], context,
                current_app=self.admin_site.name)



class ProfileAdmin(admin.ModelAdmin):
    pass

admin.site.register(Session, SessionAdmin)
admin.site.register(Profile, ProfileAdmin)

