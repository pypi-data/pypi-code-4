# -*- coding: utf-8 -*-
"""
Exemple d'un modèle de données
"""
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

from Sveetchies.django.protoforms.models import SelectionValueExtension
from Sveetchies.django.protoforms.prototypes.model_fields import ProtoZipcodeModelField, ProtoPhoneModelField, ForeignKeySelectionModelField, ManyToManySelectionModelField

class BaseContainer(models.Model):
    """
    Base d'héritage "abstraite" (sans existance concrète dans l'application) de 
    tout les modèles de contact
    
    Tout les champs définit ici seront automatiquement présents dans ses héritiers.
    """
    created = models.DateTimeField(u'date de création', auto_now_add=True)
    user_agent = models.CharField(u'user-agent', max_length=255, blank=True, null=True, editable=False)
    ip = models.IPAddressField(u'adresse IP', blank=True, null=True, editable=False)
    first_name = models.CharField(u'prénom', max_length=35, blank=False)
    last_name = models.CharField(u'nom', max_length=50, blank=False)
    email = models.EmailField(u'e-mail', blank=False)
    adress = models.TextField(u'adresse', blank=False)
    zipcode = ProtoZipcodeModelField(u'code postal', max_length=6, blank=False)
    town = models.CharField(u'ville', max_length=75, blank=False)
    phone_number = ProtoPhoneModelField(u'téléphone', max_length=20, blank=False)
    advised_from = ForeignKeySelectionModelField(u'provenance', blank=True, selectionitem_choices="advised_from")
    subscribe_newsletter = models.BooleanField(u'souhaite souscrire à la newsletter', default=False)
    extensions = generic.GenericRelation(SelectionValueExtension)

    def __unicode__(self):
        return "%s %s" % (self.first_name, self.last_name)

    class Meta:
        abstract = True
