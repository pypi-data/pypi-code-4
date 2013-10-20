# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from Sveetchies.django.gallery.models import Album, Picture

# Configs pour les vues de preview
basic_short_preview = {'default_configset_name': 'short'}
album_object_preview_kwargs = {
    'model_object': Album,
    'default_configset_name': 'short'
}
picture_object_preview_kwargs = {
    'model_object': Picture,
    'default_configset_name': 'short'
}

urlpatterns = patterns('',
    url(r'^$', 'Sveetchies.django.gallery.views.album_list', name="gallery-album-list"),
    
    url(r'^album/(?P<album_slug>[-\w]+)/$', 'Sveetchies.django.gallery.views.album_details', name="gallery-album-details"),
    
    url(r'^admin/album/preview/$', 'Sveetchies.django.pywiki2xhtml.views.preview', kwargs=basic_short_preview, name="gallery-admin-album-preview"),
    url(r'^admin/album/(?P<instance_id>\d+)/preview/$', 'Sveetchies.django.pywiki2xhtml.views.model_object_preview', kwargs=album_object_preview_kwargs, name="gallery-admin-album-object-preview"),

    url(r'^admin/picture/preview/$', 'Sveetchies.django.pywiki2xhtml.views.preview', kwargs=basic_short_preview, name="gallery-admin-picture-preview"),
    url(r'^admin/picture/(?P<instance_id>\d+)/preview/$', 'Sveetchies.django.pywiki2xhtml.views.model_object_preview', kwargs=picture_object_preview_kwargs, name="gallery-admin-picture-object-preview"),
    
    url(r'^syntax/$', 'Sveetchies.django.pywiki2xhtml.views.syntax_help_staff_member_required', name="gallery-syntax_help"),
)
