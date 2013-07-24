from django.contrib import admin
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.contrib import messages

from preferences.admin import PreferencesAdmin, csrf_protect_m

from jmbo_sitemap.models import HTMLSitemap


class HTMLSitemapAdmin(PreferencesAdmin):

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        """
        If we only have a single preference object redirect to it,
        otherwise display listing.
        """
        model = self.model
        if model.objects.all().count() > 1:
            return super(HTMLSitemapAdmin, self).changelist_view(request)
        else:
            obj = model.singleton.get()
            return redirect(reverse('admin:jmbo_sitemap_%s_change' % \
                    model._meta.module_name, args=(obj.id,)))

    def response_change(self, request, obj):
        result = super(HTMLSitemapAdmin, self).response_change(request, obj)
        if '_generate_draft' in request.POST:
            msg = _('The draft has been generated.')
            self.message_user(request, msg)
            result = HttpResponseRedirect(request.path)
        elif '_make_draft_live' in request.POST:
            msg = _('The draft has been made live.')
            self.message_user(request, msg)
            result = HttpResponseRedirect(request.path)
        return result

    def save_model(self, request, obj, form, change):
        instance = super(HTMLSitemapAdmin, self).save_model(
            request, obj, form, change
        )

        if hasattr(request, 'POST'):
            if '_generate_draft' in request.POST:
                obj.generate_draft()
            elif '_make_draft_live' in request.POST:
                obj.make_draft_live()


admin.site.register(HTMLSitemap, HTMLSitemapAdmin)
