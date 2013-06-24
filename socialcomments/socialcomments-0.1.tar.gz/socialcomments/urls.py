from django.conf.urls import patterns, include, url

urlpatterns = patterns('socialcomments.views',
	url(r'^form/$', 'form', name = 'socialcomments_ajax_form'),
	url(r'^connect/$', 'connect', name = 'socialcomments_connect'),
	url(r'^disconnect/$', 'disconnect', name = 'socialcomments_disconnect'),
	url(r'^connect/callback/$', 'callback', name = 'socialcomments_callback'),
)