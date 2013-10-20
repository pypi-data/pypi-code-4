# -*- coding: utf-8 -*-
"""
Modèles de données
"""
from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.core.cache import cache

from mptt.models import MPTTModel, TreeForeignKey
from mptt.managers import TreeManager

from Sveetchies.django.documents import (DOCUMENTS_PARSER_FILTER_SETTINGS, 
                                        DOCUMENTS_PAGE_TEMPLATES, PAGE_SLUGS_CACHE_KEY_NAME, 
                                        PAGE_RENDER_CACHE_KEY_NAME, INSERT_RENDER_CACHE_KEY_NAME,
                                        PAGE_TOC_CACHE_KEY_NAME, INSERT_TOC_CACHE_KEY_NAME)
from Sveetchies.django.documents.utils import _get_cache_keyset

DOCUMENTS_PAGE_TEMPLATES_CHOICES = [(k,v[1]) for k,v in DOCUMENTS_PAGE_TEMPLATES.items()]

DOCUMENTS_VISIBILTY_CHOICES = (
    (True, 'Visible'),
    (False, 'Non visible'),
)

class Insert(models.Model):
    """
    Document à insérer
    """
    created = models.DateTimeField(u"création", blank=True, auto_now_add=True)
    modified = models.DateTimeField(u'dernière modification', auto_now=True)
    author = models.ForeignKey(User, verbose_name="auteur")
    title = models.CharField(u"titre", blank=True, null=True, max_length=255, help_text=u"Désignation non affichée sur le site.")
    slug = models.SlugField(u'nom de raccourci', unique=True, max_length=75, help_text=u"Identifiant unique en rapport avec le titre.")
    visible = models.BooleanField(u'visible', default=True, help_text=u"Un document non visible ne sera pas affiché sur le site.")
    content = models.TextField(u"contenu", blank=False)

    def __unicode__(self):
        return self.slug
    
    def get_render_cache_key(self, **kwargs):
        """
        Renvoi la clé du cache pour le rendu du contenu
        """
        return INSERT_RENDER_CACHE_KEY_NAME.format(id=self.id, **kwargs)
    
    def get_toc_cache_key(self, **kwargs):
        """
        Renvoi la clé du cache pour le TOC du contenu
        """
        return INSERT_TOC_CACHE_KEY_NAME.format(id=self.id, **kwargs)
    
    def save(self, *args, **kwargs):
        # Invalidation de tout les clés de cache possibles pour l'objet en cas d'édition
        if self.modified:
            self.clear_cache()
        
        super(Insert, self).save(*args, **kwargs)
    
    def delete(self, using=None):
        self.clear_cache()
        super(Insert, self).delete(using=using)
    
    def clear_cache(self):
        """
        Invalidation de tout les clés de cache possibles
        """
        keys = _get_cache_keyset(INSERT_RENDER_CACHE_KEY_NAME, **{
            'id': self.id,
            'setting': DOCUMENTS_PARSER_FILTER_SETTINGS.keys(),
            'header_level': ['None']+range(1, 7),
        })
        keys += _get_cache_keyset(INSERT_TOC_CACHE_KEY_NAME, **{
            'id': self.id,
            'setting': DOCUMENTS_PARSER_FILTER_SETTINGS.keys(),
            'header_level': ['None']+range(1, 7),
        })
        cache.delete_many(keys)
        return keys
    
    class Meta:
        verbose_name = u"document à insérer"
        verbose_name_plural = u"documents à insérer"

class Page(MPTTModel):
    """
    Document pleine page
    """
    created = models.DateTimeField(u"création", blank=True)
    modified = models.DateTimeField(u'dernière modification', auto_now=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    author = models.ForeignKey(User, verbose_name="auteur")
    title = models.CharField(u"titre", blank=False, max_length=255)
    published = models.DateTimeField(u"date de publication", blank=True, help_text=u"Indique quand sera affiché le document. Laissez vide pour que le document soit affiché immédiatement, utilisez une date en avance pour programmer l'affichage d'un document dans le futur.")
    slug = models.SlugField(u'nom de raccourci', unique=True, max_length=75, help_text=u"Identifiant unique utilisé dans les URLs, en général il n'est pas utile de s'en préoccuper, il est rempli automatiquement d'après le titre.")
    template = models.CharField(u'gabarit', max_length=50, choices=DOCUMENTS_PAGE_TEMPLATES_CHOICES, default='default', help_text="Le gabarit HTML servant à afficher le contenu de cette page.")
    order = models.SmallIntegerField("ordre", default=1, help_text=u"Ordre d'affichage dans les listes et arborescences.")
    visible = models.BooleanField(u'visibilité', choices=DOCUMENTS_VISIBILTY_CHOICES, default=True, help_text=u"Un document non visible ne sera pas affiché sur le site.")
    content = models.TextField(u"contenu", blank=False)

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('documents-page-details', [self.slug])
    
    def get_template(self):
        """
        Renvoi le chemin de template configuré
        """
        return DOCUMENTS_PAGE_TEMPLATES[self.template][0]
    
    def get_render_cache_key(self, **kwargs):
        """
        Renvoi la clé du cache pour le rendu du contenu
        """
        return PAGE_RENDER_CACHE_KEY_NAME.format(id=self.id, **kwargs)
    
    def get_toc_cache_key(self, **kwargs):
        """
        Renvoi la clé du cache pour le TOC du contenu
        """
        return PAGE_TOC_CACHE_KEY_NAME.format(id=self.id, **kwargs)
    
    def save(self, *args, **kwargs):
        # TODO: modifier tout les descendants pour répercuter l'invisibilité
        # Rempli la date de publication automatique si non-remplie
        self.created = datetime.now()
        if not self.published:
            self.published = self.created
        # Invalidation de tout les clés de cache possibles pour l'objet en cas d'édition
        if self.modified:
            self.clear_cache()
        
        super(Page, self).save(*args, **kwargs)
    
    def delete(self, using=None):
        self.clear_cache()
        super(Page, self).delete(using=using)
    
    def clear_cache(self):
        """
        Invalidation de tout les clés de cache possibles liés à la page
        """
        keys = _get_cache_keyset(PAGE_RENDER_CACHE_KEY_NAME, **{
            'id': self.id,
            'setting': DOCUMENTS_PARSER_FILTER_SETTINGS.keys(),
        })
        keys += _get_cache_keyset(PAGE_TOC_CACHE_KEY_NAME, **{
            'id': self.id,
            'setting': DOCUMENTS_PARSER_FILTER_SETTINGS.keys(),
        })
        cache.delete_many([PAGE_SLUGS_CACHE_KEY_NAME]+keys)
        return keys
    
    class Meta:
        verbose_name = u"page"
        verbose_name_plural = u"pages"
    
    class MPTTMeta:
        order_insertion_by = ['order', 'title']
