# -*- coding: utf-8 -*-
"""
Modèles de données
"""
from django.db import models
from django.contrib.auth.models import User

from Sveetchies.django.filefield import content_file_name
from Sveetchies.django.gallery import GALLERY_ALBUM_THUMB_UPLOADPATH, GALLERY_PICTURE_LARGE_UPLOADPATH, GALLERY_PICTURE_THUMB_UPLOADPATH

from managers import PictureManager

GALLERY_ALBUM_THUMB_UPLOADTO = lambda instance,filename: content_file_name(GALLERY_ALBUM_THUMB_UPLOADPATH, instance, filename)
GALLERY_PICTURE_LARGE_UPLOADTO = lambda instance,filename: content_file_name(GALLERY_PICTURE_LARGE_UPLOADPATH, instance, filename)
GALLERY_PICTURE_THUMB_UPLOADTO = lambda instance,filename: content_file_name(GALLERY_PICTURE_THUMB_UPLOADPATH, instance, filename)

"""
TODO: Méthodes de saves pour l'adaptation à la volée des images et remplissage 
      automatique des vignettes (à partir de leur version originale) non remplis.
"""

class Album(models.Model):
    """
    Album d'images
    """
    create_date = models.DateTimeField(u"création", auto_now_add=True)
    author = models.ForeignKey(User, verbose_name="auteur", related_name="gallery_album_author")
    slug = models.SlugField(u'nom de raccourci', unique=True, max_length=50, help_text=u"Identifiant unique utilisé dans les URLs, en général il n'est pas utile de s'en préoccuper, il est rempli automatiquement d'après le titre. Si le formulaire renvoi une erreur à ce sujet, modifiez juste la fin de en y insérant des caractères au hasard (par exemple quelques chiffres) jusqu'à ce que soit bon. Vous pouvez aussi l'arranger selon vos besoins. Sachez qu'étant utilisé dans les urls, un raccourci a un effet positif sur le référencement.")
    title = models.CharField(u"titre", blank=False, max_length=255, unique=True)
    thumb = models.ImageField(u'vignette', upload_to=GALLERY_ALBUM_THUMB_UPLOADTO, max_length=255, height_field='thumb_height', width_field='thumb_width', blank=False)
    thumb_width = models.IntegerField() 
    thumb_height = models.IntegerField()
    description = models.TextField(u"description", blank=True)
    visible = models.BooleanField(u'visible', default=True, help_text=u"Un album non visible ne sera pas affiché sur le site ni son contenu. Une façon d'archiver sans supprimer.")

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('gallery-album-details', [self.slug])
    
    class Meta:
        verbose_name = u"album"
        verbose_name_plural = u"albums"

class Picture(models.Model):
    """
    Image
    """
    create_date = models.DateTimeField(u"création", auto_now_add=True)
    author = models.ForeignKey(User, verbose_name="auteur", related_name="gallery_picture_author")
    album = models.ForeignKey(Album, verbose_name=u"album", help_text=u"L'album où sera affichée l'image.")
    visible = models.BooleanField(u'visible', default=True, help_text=u"Une image non visible ne sera pas affichée sur le site. Une façon d'archiver sans supprimer.")
    title = models.CharField(u"titre", blank=False, max_length=255, help_text=u"Essayez de garder vos titres uniques de façon à optimiser le référencement et la pertinence.")
    description = models.TextField(u"description", blank=True, help_text=u"Texte de description optionnel.")
    thumb = models.ImageField(u'vignette', upload_to=GALLERY_PICTURE_THUMB_UPLOADTO, max_length=255, blank=True, null=True, height_field='thumb_height', width_field='thumb_width', help_text="Optionnel, si non-rempli, une vignette sera automatiquement crée à partir de la version originale.")
    thumb_width = models.IntegerField(default=0)
    thumb_height = models.IntegerField(default=0)
    large = models.ImageField(u'image', upload_to=GALLERY_PICTURE_LARGE_UPLOADTO, max_length=255, height_field='large_height', width_field='large_width', blank=False)
    large_width = models.IntegerField(default=0)
    large_height = models.IntegerField(default=0)
    objects = PictureManager()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('news-entry-details', [self.category.slug, self.slug])
    
    class Meta:
        verbose_name = u"image"
        verbose_name_plural = u"images"

