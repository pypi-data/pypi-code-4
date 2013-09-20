
from django.conf.urls.defaults import *

from nano.badge.models import *

urlpatterns = patterns('nano.mark.views',
        url(r'^toggle$',                  'toggle_mark', {}, 'toggle_mark'),
)
