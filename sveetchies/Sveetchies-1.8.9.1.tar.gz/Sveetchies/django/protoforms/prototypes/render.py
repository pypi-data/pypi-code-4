# -*- coding: utf-8 -*-
from django.db import models
from django.core.validators import EMPTY_VALUES
from django.template import loader as template_loader
from django.template import Context as template_Context
from django.template.defaultfilters import capfirst

from Sveetchies.django.protoforms.models import SelectionItem

from Sveetchies.django.protoforms import PROTO_EXTENDED_VALUE_FIELD_KEY
from Sveetchies.django.protoforms.prototypes.model_fields import ForeignKeySelectionModelField, ManyToManySelectionModelField

class RenderForm(object):
    """
    Rendu d'affichage des données d'un objet d'après son modèle
    """
    excluded = ['advised_from', 'subscribe_newsletter']
    def __init__(self, model, datas_object):
        self.model = model
        self.datas_object = datas_object
        self.order = self.model.objects.get_all_order()
        self.schemes = dict( self.model.objects.get_all_shemes() )
        self.datas_table = self.map_datas(datas_object)
    
    def plain(self):
        """
        Rendu basique en plain/text
        """
        output = []
        for label, value, extra in self.datas_table:
            label = label.replace('&#160;', '')
            if value not in EMPTY_VALUES:
                if extra:
                    value = "%s; %s" % (value, extra)
                output.append(u"%s : %s" % (capfirst(label), value))
        return u'\n\n'.join(output)
    
    def is_extension_modelfield(self, form_field_name, form_field_object):
        """
        Test qu'un champ de modèle est une liste de séléction
        """
        extension_fieldname = PROTO_EXTENDED_VALUE_FIELD_KEY % form_field_name
        if isinstance(form_field_object, ForeignKeySelectionModelField) or isinstance(form_field_object, ManyToManySelectionModelField):
            try:
                ext = SelectionItem.objects.get(kind=form_field_object.collectorform_selectionitem_kind, value_extended=True)
            except SelectionItem.DoesNotExist:
                pass
            else:
                return form_field_name, extension_fieldname, ext.key
        return None
    
    def map_datas(self, model_object):
        """
        Transformation des données soumis en un rendu texte "label: value"
        """
        output = []
        form_map = {}
        
        # Cartographie de tout les champs toute étapes confondus et récupération des 
        # labels customisés pour ceux qui en ont un
        for item in self.model._meta.fields:
            if not isinstance(item, models.fields.AutoField):
                form_map[item.name] = (item, item.verbose_name)
                if item.name in self.schemes and 'label' in self.schemes[item.name]:
                    form_map[item.name] = (item, self.schemes[item.name]['label'])
        # Récupère aussi les m2m qui ne sont pas répertoriés dans 
        # ``self.model._meta.fields``
        if hasattr(self.model._meta, 'many_to_many'):
            for item in self.model._meta.many_to_many:
                if isinstance(item, ManyToManySelectionModelField):
                    form_map[item.name] = (item, item.verbose_name)
                    if item.name in self.schemes and 'label' in self.schemes[item.name]:
                        form_map[item.name] = (item, self.schemes[item.name]['label'])
        
        # Créé une map des données prête à la mise en forme
        for item in self.order:
            if item in self.excluded:
                continue
            if hasattr(self.datas_object, item):
                value = data_value = getattr(self.datas_object, item)
                extension = None
                extended = self.is_extension_modelfield(item, form_map[item][0])
                # Vérifie que le champs est une liste de séléction étendue par valeur 
                # manuelle
                if extended != None:
                    if data_value:
                        # Vérifie que le champs n'est pas une valeur à étendre
                        value = data_value.label
                        if data_value.key == extended[2]:
                            extension = self.datas_object.extensions.get(extended_field=item).value
                elif hasattr(model_object, "get_%s_display"%item):
                    value = getattr(model_object, "get_%s_display"%item)()
                
                output.append( (form_map[item][1], self.correct_value(value), extension) )
        
        return output
    
    def correct_value(self, value):
        """
        Transcription des valeurs qui ne sont pas des strings
        """
        if isinstance(value, bool):
            value = "Oui"
            if value == False:
                value = "Non"
        elif isinstance(value, SelectionItem):
            value = value.label
        # La seule technique simple trouvée pour détecter le "ManyRelatedManager"
        # TODO: should be buggy with "normal" ManyToMany
        elif hasattr(value, 'symmetrical'):
            value = ', '.join([item.label for item in value.all()])
        elif value == None:
            value = ''
        elif not isinstance(value, basestring):
            value = str(value)
        return value
