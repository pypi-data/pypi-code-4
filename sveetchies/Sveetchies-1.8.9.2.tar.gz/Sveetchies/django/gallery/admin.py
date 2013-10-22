# -*- coding: utf-8 -*-
"""
Map des modèles de données dans l'administration de Django

TODO: Important, lors d'une édition, empecher le redimensionnement automatique si 
      l'image n'a pas changé 
"""
import os

from django.conf import settings
from django.contrib import admin

from models import *

from Sveetchies.django.gallery import (
    GALLERY_ALBUM_THUMB_LAYOUT,
    GALLERY_PICTURE_THUMB_LAYOUT,
    GALLERY_PICTURE_LARGE_LAYOUT,
    GALLERY_ALBUM_THUMB_UPLOADPATH,
    GALLERY_PICTURE_LARGE_UPLOADPATH,
    GALLERY_PICTURE_THUMB_UPLOADPATH
)
from Sveetchies.django.gallery.utils import adapt_source

class AlbumAdmin(admin.ModelAdmin):
    list_display = ('title', 'visible', 'author', 'create_date')
    list_filter = ('visible',)
    ordering = ('title',)
    search_fields = ('title','description',)
    readonly_fields = ('author',)
    list_display_links = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = [
        (u'Contenu', {'fields': ('title', 'thumb', 'description')}),
        (u'Paramètres', {'classes': ('collapse open',), 'fields': ('slug', 'visible',)}),
    ]
    
    def save_model(self, request, obj, form, change):
        tmp_thumb = None
        deprecated_thumb = None
        if 'thumb' in form.changed_data and 'thumb' in form.initial:
            deprecated_thumb = form.initial['thumb'].path
        
        # Récupère l'instance finalisée du formulaire
        instance = form.save(commit=False)
        # Assignation automatique de l'auteur
        instance.author = request.user
        instance.save()
        form.save_m2m()
        
        # Redimensionne la vignette en cas d'un nouvel objet ou pendant l'édition si 
        # elle a changée
        if not change or deprecated_thumb:
            tmp_thumb = instance.thumb.path
            instance.thumb = adapt_source(tmp_thumb, GALLERY_ALBUM_THUMB_UPLOADPATH, GALLERY_ALBUM_THUMB_LAYOUT)
            instance.save()
            os.remove(tmp_thumb)
            if change and deprecated_thumb:
                os.remove(deprecated_thumb)

        return instance

class PictureAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'album', 'visible', 'create_date')
    list_filter = ('visible', 'album')
    ordering = ('album',)
    search_fields = ('title','description',)
    raw_id_fields = ('album',)
    readonly_fields = ('author',)
    list_display_links = ('title',)
    fieldsets = [
        (u'Paramètres', {'classes': ('collapse open',), 'fields': ('album', 'visible')}),
        (u'Fichiers', {'fields': ('thumb','large',)}),
        (u'Informations', {'fields': ('title', 'description')}),
    ]
    
    def save_model(self, request, obj, form, change):
        """
        Si ajout :
            * Si vignette, redimensionnement et assignation;
            * Si pas vignette, utiliser la version large comme source, redimensionner et assigner;
        Si modif :
            * Si vignette et large non changés, pas toucher;
            * Si vignette modifiée, redimensionner et assigner;
            * Si large modifiée mais pas vignette, utiliser large comme source de nouvelle vignette, redimensionner et assigner;
            * Si large et vignette modifiée, redimensionner et assigner chacun séparément;
            
        La vignette est donc automatisée, si l'user veut en forcer une nouvelle en 
        changeant la large, il doit uploader la vignette en meme temps ou dans un second temps.
        
        Si il voulait la conserver, il devra la mettre de coté manuellement sur son 
        propre disque dur temporairement et la réuploader le moment voulu.
        """
        tmp_large = None
        tmp_thumb = None
        deprecated_thumb = None
        deprecated_large = None
        if 'thumb' in form.changed_data and 'thumb' in form.initial:
            deprecated_thumb = form.initial['thumb'].path
        if 'large' in form.changed_data and 'large' in form.initial:
            deprecated_large = form.initial['large'].path
        
        # Récupère l'instance finalisée du formulaire
        instance = form.save(commit=False)
        # Assignation automatique de l'auteur
        instance.author = request.user
        instance.save()
        form.save_m2m()
        
        # Redimensionne l'image "large"
        if not change or deprecated_large:
            tmp_large = instance.large.path
            instance.large = adapt_source(tmp_large, GALLERY_PICTURE_LARGE_UPLOADPATH, GALLERY_PICTURE_LARGE_LAYOUT)
        
        source_thumb = None
        # Formulaire de création
        if not change:
            # Vignette spécifiée
            if instance.thumb:
                source_thumb = instance.thumb.path
                tmp_thumb = instance.thumb.path
            # Pas de vignette spécifiée, utilise la version "large" comme source
            else:
                source_thumb = tmp_large
        # Formulaire d'édition, vignette spécifiée
        elif deprecated_thumb:
            source_thumb = instance.thumb.path
            tmp_thumb = source_thumb
        # Formulaire d'édition, pas de vignette spécifiée, mais version "large" modifiée, 
        # utilise la version "large" comme source
        elif deprecated_large and not deprecated_thumb:
            source_thumb = tmp_large
        # Redimensionne la vignette séléctionnée le cas échéant
        if source_thumb:
            instance.thumb = adapt_source(source_thumb, GALLERY_PICTURE_THUMB_UPLOADPATH, GALLERY_PICTURE_THUMB_LAYOUT)
        
        # Save et nettoyage de l'ancienne image
        instance.save()
        if tmp_large:
            os.remove(tmp_large)
        if tmp_thumb:
            os.remove(tmp_thumb)
        if deprecated_thumb:
            os.remove(deprecated_thumb)
        if deprecated_large:
            os.remove(deprecated_large)

        return instance

admin.site.register(Album, AlbumAdmin)
admin.site.register(Picture, PictureAdmin)
