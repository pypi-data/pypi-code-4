from django.conf.urls import patterns
from django.conf.urls import url

from django_relinking import views

urlpatterns = patterns(
    '',
    url(r'^get_content_type_objects/$', views.get_objects, name="get_content_type_objects"),
)
