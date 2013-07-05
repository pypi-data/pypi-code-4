from django.conf.urls import patterns, include, url
from .views import contactForm
from django.views.generic import TemplateView


urlpatterns = patterns('',
	url(r'^contact/$', contactForm),
	url(r'^contact/thanks/$', TemplateView.as_view(template_name='thanks.html'), name="thanks")
)

