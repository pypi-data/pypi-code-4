from django.conf.urls import patterns, url
from preprocessors.validation import validate_form

urlpatterns = patterns(
    '',
    url(r'^validate-form/$', validate_form, name='validate-form'),
)
