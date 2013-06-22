__all__ = ('urlpatterns',)

from django.conf.urls.defaults import *

urlpatterns = patterns('admin_timeline.views',
    url(r'^$', view='log', name='admin_timeline.log'),
)
