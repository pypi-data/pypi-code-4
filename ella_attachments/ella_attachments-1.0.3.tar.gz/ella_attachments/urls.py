from django.template.defaultfilters import slugify
from django.utils.translation import ugettext as _

try:
    from django.conf.urls import patterns, url
except ImportError:  # Django < 1.4
    from django.conf.urls.defaults import patterns, url


from ella_attachments.views import download_attachment

urlpatterns = patterns('',
    url(r'^%s/(?P<slug>.*)' % slugify(_('download')), download_attachment, name='ella_attachments-download'),
)
