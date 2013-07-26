# -*- coding: utf-8 -*-
import datetime

from django.template import RequestContext
from django.shortcuts import get_object_or_404, render_to_response
from django.views.generic.list_detail import object_list

from Sveetchies.django.gallery import GALLERY_ALBUMS_PAGINATION, GALLERY_PICTURES_PAGINATION
from Sveetchies.django.gallery.models import Album, Picture

def album_list(request):
    """
    Liste des Albums
    """
    template = 'gallery/album_list.html'

    albums_queryset = Album.objects.filter(visible=True).order_by('-create_date')
    
    response = object_list(
        request,
        queryset=albums_queryset,
        paginate_by=GALLERY_ALBUMS_PAGINATION,
        template_name=template,
        #extra_context=extra_context,
        allow_empty=True
    )
    return response

def album_details(request, album_slug):
    """
    Album détails et liste de ses images
    """
    template = 'gallery/album_details.html'

    album_object = get_object_or_404(Album, visible=True, slug=album_slug)
    
    entries_queryset = album_object.picture_set.publishable_filter().order_by('create_date')
    
    extra_context = {
        'album_object': album_object,
    }
    
    response = object_list(
        request,
        queryset=entries_queryset,
        paginate_by=GALLERY_PICTURES_PAGINATION,
        template_name=template,
        extra_context=extra_context,
        allow_empty=True
    )
    return response

#def picture_details(request, album_slug, picture_id):
    #"""
    #Détails image
    #"""
    #template = 'gallery/picture_details.html'

    #picture_object = Entry.objects.get_publishable_or_404(album__slug=album_slug, pk=picture_id)
    
    #extra_context = {
        #'album_object': picture_object.album,
        #'picture_object': picture_object,
    #}
    
    #return render_to_response(template, extra_context, context_instance=RequestContext(request))
