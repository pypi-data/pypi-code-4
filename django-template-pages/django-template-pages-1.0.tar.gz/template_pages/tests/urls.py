from django.conf.urls import include, patterns, url

urlpatterns = patterns('',
    url(ur'^', include('template_pages.urls')),
)
