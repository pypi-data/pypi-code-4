# -*- coding: utf-8 -*-
"""
Brique d'albums d'images/photos

============
Installation
============

Requis :

* Django >= 1.3.x

Ce module est à déclarer comme application d'un projet Django dans 
``settings.INSTALLED_APPS`` tel que : ::

    INSTALLED_APPS = (
        'Sveetchies.django.gallery',
        ...
        'yourapps'
    )

TODO: * Le code qui fait le redimensionnement devrait pouvoir utiliser un pointeur de 
        fichier comme source au lieu d'un chemin de fichier, histoire de pouvoir passer 
        le pointeur d'un meme fichier pour plusieurs redimensionnement à la suite sans 
        consommer une nouvelle ouverture de fichier à chaque fois;
      * L'implémentation du redimensionnement dans l'admin est un peu "tordue", le 
        processus est effectuée après la sauvegarde et que le fichier uploadé ait été 
        écrit sur le FS, ensuite le traitement est fait et le fichier uploadé est écrasé 
        par le nouveau;
      * Un nouveau fichier est écrit même si le redimensionnement n'est pas nécessaire, 
        alors qu'il devrait y avoir au moins une option pour l'empêcher et simplement 
        conserver l'original;
      * Le format des images redimensionnés est toujours JPEG donc par exemple les GIF 
        animés ne fonctionnent pas;
"""
from django.conf import settings
from django import template

__version__ = '0.1.1'

IMAGE_FORMATS_CHOICES = getattr(settings, 'IMAGE_FORMATS_CHOICES', {
    'JPEG': 'jpg',
    'GIF': 'gif',
    'PNG': 'png',
})
IMAGE_FORMAT_DEFAULT = getattr(settings, 'IMAGE_FORMAT_DEFAULT', 'JPEG')

GALLERY_ALBUMS_PAGINATION = getattr(settings, 'GALLERY_ALBUMS_PAGINATION', 15)
GALLERY_PICTURES_PAGINATION = getattr(settings, 'GALLERY_PICTURES_PAGINATION', 20)

GALLERY_ALBUM_WIDGET_TEMPLATE = getattr(settings, 'GALLERY_ALBUM_WIDGET_TEMPLATE', 'gallery/album_widget.html')

GALLERY_ALBUM_THUMB_UPLOADPATH = getattr(settings, 'GALLERY_ALBUM_THUMB_UPLOADPATH', 'gallery/album_thumb/%Y/%m/%d')
GALLERY_PICTURE_LARGE_UPLOADPATH = getattr(settings, 'GALLERY_PICTURE_LARGE_UPLOADPATH', 'gallery/large/%Y/%m/%d')
GALLERY_PICTURE_THUMB_UPLOADPATH = getattr(settings, 'GALLERY_PICTURE_THUMB_UPLOADPATH', 'gallery/thumb/%Y/%m/%d')

GALLERY_ALBUM_THUMB_LAYOUT = getattr(settings, 'GALLERY_ALBUM_THUMB_LAYOUT', 'Square(128x128)')
GALLERY_PICTURE_THUMB_LAYOUT = getattr(settings, 'GALLERY_PICTURE_THUMB_LAYOUT', 'Square(160x160)')
GALLERY_PICTURE_LARGE_LAYOUT = getattr(settings, 'GALLERY_PICTURE_LARGE_LAYOUT', 'Square(900x900)')

template.add_to_builtins("Sveetchies.django.tags.pagination")
