# -*- coding: utf-8 -*-
"""
Modèles de données
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from Sveetchies.django.protoforms import PROTO_SELECTION_KEY_LENGTH, PROTO_SELECTION_KINDS

class SelectionValueExtension(models.Model):
    """
    Extension d'une valeure de séléction
    
    Sert par exemple à disposer un champ de saisie texte pour rentrer une 
    valeur manuelle lors de la séléction d'un choix du genre "Autre".
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    extended_field = models.CharField(u'nom du champ étendu', max_length=100, blank=False)
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    created = models.DateTimeField(u'date de création', auto_now_add=True)
    value = models.CharField(u'valeur', max_length=100, blank=False)

class SelectionItem(models.Model):
    """
    Élément d'une liste de choix d'un champ de contact
    """
    created = models.DateTimeField(u'date de création', auto_now_add=True)
    kind = models.CharField(u'type de liste', max_length=30, choices=PROTO_SELECTION_KINDS, blank=False)
    key = models.SlugField(u'clé d\'identification', max_length=PROTO_SELECTION_KEY_LENGTH, blank=False)
    label = models.CharField(u'label affiché', max_length=255, blank=False)
    order = models.IntegerField(u'ordre d\'affichage', max_length=5, default=0)
    value_extended = models.BooleanField(u'valeur manuelle requise', default=False)

    def __unicode__(self):
        return self.label
    
    class Meta:
        verbose_name = u"Choix de séléction"
        verbose_name_plural = u"Liste de choix de séléctions"
