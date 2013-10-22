# -*- coding: utf-8 -*-
#
# Template tags pour les catégories et billets
#
from django import template
from django.utils.safestring import mark_safe

from Sveetchies.imaging.picture import PictureLayout
from Sveetchies.django.utils import get_string_or_variable
from Sveetchies.django.gallery import GALLERY_ALBUM_WIDGET_TEMPLATE
from Sveetchies.django.gallery.models import Album, Picture

register = template.Library()

@register.simple_tag
def adapt_to_layout(imageObj, layout, mode="html"):
    layout = PictureLayout.from_layout(layout)
    newsize = layout.get_size_from((imageObj.width, imageObj.height))
    if mode == "width":
        return str(newsize[0])
    elif mode == "height":
        return str(newsize[1])
    elif mode == "css":
        return ' width:{0}px;height:{1}px;'.format(*newsize)
    else:
        return ' width="{0}" height="{1}"'.format(*newsize)

@register.tag(name="random_pictures")
def do_random_pictures(parser, token):
    """
    Lecture de préparation du Tag
   
    Images tout album : ::
    
        {% random_pictures limit %}
    
    Images de l'album 'album_id' : ::
    
        {% random_pictures limit album_id %}
    
    Avec un template personnalisé : ::
    
        {% random_pictures limit None template_path %}
    
    """
    args = token.split_contents()
    if args < 2:
        raise template.TemplateSyntaxError, "You need to specify a limit"
    else:
        return random_pictures_view(*args[1:])

class random_pictures_view(template.Node):
    """
    Génération du rendu html du tag "random_pictures"
    """
    def __init__(self, limit, album_id=None, templatepath=None):
        self.limit = limit
        self.album_id = album_id
        self.templatepath = templatepath
    
    def render(self, context):
        string = ''
        album_object = None
        limit = get_string_or_variable(self.limit, context, capture_none_value=False)
        
        album_id = get_string_or_variable(self.album_id, context, capture_none_value=True)
        if album_id:
            if album_id == 'last':
                album_object = Album.objects.filter(visible=True).order_by('-create_date')
                if album_object.count() == 0:
                    return ''
                else:
                    album_object = album_object[0]
            else:
                try:
                    album_object = Album.objects.get(visible=True, pk=int(album_id))
                except Album.DoesNotExist:
                    return ''
        
        templatepath = GALLERY_ALBUM_WIDGET_TEMPLATE
        if self.templatepath:
            templatepath = get_string_or_variable(self.templatepath, context, capture_none_value=True)
        
        pictures_queryset = Picture.objects.publishable_filter()
        if album_object:
            pictures_queryset = pictures_queryset.filter(album=album_object)
        pictures_queryset = pictures_queryset.order_by('?')[:limit]
            
        context.update({
            'random_pictures_limit' : limit,
            'random_pictures_album_object' : album_object,
            'random_pictures_object_list' : pictures_queryset,
        })
        string = template.loader.get_template(templatepath).render(template.Context(context))
        
        return mark_safe( string )
