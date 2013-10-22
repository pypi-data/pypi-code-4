# -*- coding: utf-8 -*-
"""
Modèles de données
"""
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User

from Sveetchies.django.attachments.models import Attach
from managers import EntryManager

class Category(models.Model):
    """
    Catégorie
    """
    create_date = models.DateTimeField(u"création", auto_now_add=True)
    slug = models.SlugField(u'nom de raccourci', unique=True, max_length=50, help_text=u"Identifiant unique utilisé dans les URLs, en général il n'est pas utile de s'en préoccuper, il est rempli automatiquement d'après le titre. Si le formulaire renvoi une erreur à ce sujet, modifiez juste la fin de en y insérant des caractères au hasard (par exemple quelques chiffres) jusqu'à ce que soit bon. Vous pouvez aussi l'arranger selon vos besoins. Sachez qu'étant utilisé dans les urls, un raccourci a un effet positif sur le référencement.")
    title = models.CharField(u"titre", blank=False, max_length=255, unique=True)
    description = models.TextField(u"description", blank=True)
    visible = models.BooleanField(u'visible', default=True, help_text=u"Une catégorie non visible ne sera pas affiché sur le site ni ses billets. Une façon d'archiver sans supprimer.")

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('news-category-details', [self.slug])
    
    class Meta:
        verbose_name = u"catégorie"
        verbose_name_plural = u"catégories"

class Entry(models.Model):
    """
    Billet
    """
    author = models.ForeignKey(User, verbose_name="auteur", related_name="news_entry_author")
    create_date = models.DateTimeField(u"création", auto_now_add=True)
    publish_date = models.DateTimeField(u"date de publication", blank=True, help_text=u"La date de publication indique quand sera affiché le billet. Laissez vide pour que le billet soit affiché immédiatement, utilisez une date en avance pour programmer l'affichage d'un billet dans le futur.")
    category = models.ForeignKey(Category, verbose_name=u"catégorie", help_text=u"La catégorie où sera affiché le billet.")
    slug = models.SlugField(u'nom de raccourci', unique=True, max_length=75, help_text=u"Identifiant unique utilisé dans les URLs, en général il n'est pas utile de s'en préoccuper, il est rempli automatiquement d'après le titre. Si le formulaire renvoi une erreur à ce sujet, modifiez juste la fin de en y insérant des caractères au hasard (par exemple quelques chiffres) jusqu'à ce que soit bon. Vous pouvez aussi l'arranger selon vos besoins. Sachez qu'étant utilisé dans les urls, un raccourci a un effet positif sur le référencement.")
    title = models.CharField(u"titre", blank=False, max_length=255, help_text=u"Essayez de garder vos titres uniques de façon à optimiser le référencement et la pertinence.")
    visible = models.BooleanField(u'visible', default=True, help_text=u"Un billet non visible ne sera pas affiché sur le site. Une façon d'archiver sans supprimer.")
    introduction = models.TextField(u"introduction", blank=True, help_text=u"Si une introduction existe, elle sera affichée dans les listes à la place du contenu et il faudra cliquer sur le lien pour lire la totalité du billet (introduction et contenu à la suite).")
    content = models.TextField(u"contenu", blank=False)
    attached_files = models.ManyToManyField(Attach, verbose_name="Fichiers", blank=True, help_text="Séléctionnez les fichiers que vous souhaitez attacher au billet, pour transférer un nouveau fichier dans cette liste, utilisez l'icône <strong>+</strong>. <br/><br/><ins><strong>Les nouveaux fichiers ne seront pris en compte par l'éditeur que lorsque vous aurez enregistré les modifications</strong></ins>.<br/><br/>")
    display_attachs = models.BooleanField(u'listage des fichiers', default=False, help_text=u"Indique si la liste des fichiers attachés doit être affichée au bas du billet.")
    objects = EntryManager()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('news-entry-details', [self.category.slug, self.slug])
    
    def is_collapsed_in_list(self):
        return not(self.introduction.strip() == '')
    is_collapsed_in_list.boolean = True
    is_collapsed_in_list.short_description = 'En lire plus'

    def get_attachments(self, user=None):
        """
        Renvoi une liste des fichiers attachés au document, optionnellement limitée aux 
        droits d'un objet utilisateur
        """
        cache_key = "_get_attachments_cache_for_staff_%s" % str(user and user.is_staff)
        if not hasattr(self, cache_key):
            query_kwargs = {
                'archived':False,
            }
            if user and not user.is_staff:
                query_kwargs['is_public'] = True
            attachments = self.attached_files.filter(**query_kwargs).order_by('title')
            setattr(self, cache_key, attachments)
        return getattr(self, cache_key)
    
    def save(self):
        # Date de publication automatique si non-remplie
        if not self.publish_date:
            self.publish_date = datetime.now()
        
        super(Entry, self).save()
    
    class Meta:
        verbose_name = u"billet"
        verbose_name_plural = u"billets"
