from django.conf.urls import patterns, include, url
from contact.views import contactForm



urlpatterns = patterns('',

	url(r'^contact/$', contactForm),
)

