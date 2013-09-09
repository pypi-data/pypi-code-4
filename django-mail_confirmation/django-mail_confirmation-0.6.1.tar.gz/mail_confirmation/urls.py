from django.conf.urls import patterns, url
from .views import Confirm


urlpatterns = patterns('',
                       url(r'^(?P<confirmationid>\w+)$', Confirm.as_view(), name='url'),

)
