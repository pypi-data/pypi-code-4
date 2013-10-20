# -*- coding: utf-8 -*-
"""
Modèles de données des différents formulaires pour collecter des demandes d'informations
"""
from django.db import models

from Sveetchies.django.protoforms.models import SelectionItem

class ForeignKeySelectionModelField(models.ForeignKey):
    """
    Champ de séléction d'après SelectionItem
    """
    def __init__(self, verbose_name, custom_key=None, to_field=None, rel_class=models.fields.related.ManyToOneRel, **kwargs):
        self.collectorform_selectionitem_kind = kwargs['selectionitem_choices']
        del kwargs['selectionitem_choices']
        # Par défaut le champ utilise le nom clé de sa liste de séléction
        key = self.collectorform_selectionitem_kind
        # Nom clé customisé (pour différer de celui de sa liste)
        if custom_key:
            key = custom_key
        # Attributs du champ
        if kwargs.get('blank', False):
            kwargs['null'] = True
        kwargs['verbose_name'] = verbose_name
        kwargs['limit_choices_to'] = {'kind': self.collectorform_selectionitem_kind}
        kwargs['related_name'] = "%%(app_label)s_%%(class)s_%s_related" % key
        
        super(ForeignKeySelectionModelField, self).__init__(SelectionItem, to_field=to_field, rel_class=rel_class, **kwargs)

class ManyToManySelectionModelField(models.ManyToManyField):
    """
    Champ de séléction multiple d'après SelectionItem
    
    TODO: * Il faudrait lever une exception de modèle invalide lorsque 
            "selectionitem_choices" n'est pas rempli car bien qu'en argument nommé il est 
            obligatoire.
            Le même principe se reporte sur "ForeignKeySelectionModelField" et à priori 
            aussi sur leur version de "*FormField".
          * Non testé avec une valeur étendue;
          * Aucune idée de l'intéraction avec un vrai champ ManyToMany dans le même modèle;
    """
    def __init__(self, verbose_name, custom_key=None, selectionitem_choices=None, **kwargs):
        self.collectorform_selectionitem_kind = selectionitem_choices
        # Par défaut le champ utilise le nom clé de sa liste de séléction
        key = self.collectorform_selectionitem_kind
        # Nom clé customisé (pour différer de celui de sa liste)
        if custom_key:
            key = custom_key
        # Attributs du champ
        if kwargs.get('blank', False):
            kwargs['null'] = True
        kwargs['verbose_name'] = verbose_name
        kwargs['limit_choices_to'] = {'kind': self.collectorform_selectionitem_kind}
        kwargs['related_name'] = "%%(app_label)s_%%(class)s_%s_related" % key
        
        super(ManyToManySelectionModelField, self).__init__(SelectionItem, **kwargs)

class ProtoZipcodeModelField(models.CharField):
    """
    Champ de code postal
    
    Simple héritage de ``Charfield`` sans rien modifier, juste pour avoir une signature 
    explicite.
    """
    pass

class ProtoPhoneModelField(models.CharField):
    """
    Champ d'un numéro de téléphone
    
    Simple héritage de ``Charfield`` sans rien modifier, juste pour avoir une signature 
    explicite qui permet au formulaire de le détecter et le transformer en un champ de 
    téléphone avec ``django.contrib.localflavor``.
    """
    pass
