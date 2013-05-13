"""URLs of the ``cmsplugin_blog_language_publish`` app. """
from django.conf.urls.defaults import include, patterns, url

urlpatterns = patterns(
    url(r'^', include('cmsplugin_blog.urls')),
)
