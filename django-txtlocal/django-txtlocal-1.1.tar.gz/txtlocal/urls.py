from django.conf.urls.defaults import *

urlpatterns = patterns(
    'txtlocal.views',
    url(r'^$', 'sms_response', name='sms_response'),
)
