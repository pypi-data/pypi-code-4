from django.conf.urls import patterns, include, url
from .views import contactForm



urlpatterns = patterns('',
	url(r'^contact/$', contactForm),
)

