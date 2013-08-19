from django.conf.urls.defaults import url, patterns
from .views import SetFullCookie

urlpatterns = patterns(
    '',
    url(r'^full/on/$', SetFullCookie.as_view(value = True), name = 'on'),
    url(r'^full/off/$', SetFullCookie.as_view(value = False), name = 'off'),
)    
