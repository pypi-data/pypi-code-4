# -*- coding: utf-8 -*-
from django.db import models
from django.forms import widgets

from Sveetchies.django.protoforms.prototypes.widgets import ProtoCheckboxSelectMultiple

class SchemaFormError(Exception):
    pass

class BaseContainerManager(models.Manager):
    """
    Manager de base
    """
    def is_exportable(self):
        """
        Permet d'indiquer que le modèle est exportable depuis l'admin, à écraser dans 
        le manager du modèle en retournant False pour empêcher qu'il soit exportable.
        """
        return True
    
    def get_form_fields_order(self, step=1):
        """
        Renvoi la liste d'ordre d'affichage des champs du formulaire pour l'étape donnée
        """
        scheme = getattr(self, 'form_display_scheme_step_%s'%step, None)
        if scheme:
            return [item[0] for item in scheme]
        return None

    def get_form_fields_exclude(self, step=1):
        """
        Renvoi une liste d'exclusion de champs à partir de la liste des champs du modèle 
        moins ceux listés dans le schéma de mise en forme
        """
        excludes = ()
        order = self.get_form_fields_order(step=step)
        model_fieldnames = [item.name for item in self.model._meta.fields if item.name != 'id']
        if order:
            excludes = [excluded_name for excluded_name in model_fieldnames if excluded_name not in order]
        return excludes

    def get_form_fields_widget(self, step=1):
        """
        Renvoi un dictionnaire des widgets à forcer pour certains champs
        
        Lève une exception si le nom d'un widget invoqué n'existe pas.
        """
        widgets_scheme = {}
        scheme = getattr(self, 'form_display_scheme_step_%s'%step, None)
        if scheme:
            for k,v in dict(scheme).items():
                if 'widget' in v:
                    widgets_scheme[k] = self.get_widget_instance(v['widget'])
            
        return widgets_scheme

    def get_widget_instance(self, widget_params, kwargs={}):
        """
        Renvoi le widget initialisé d'un champ
        """
        if isinstance(widget_params, basestring):
            widget_name = widget_params
        elif isinstance(widget_params, tuple) or isinstance(widget_params, list):
            widget_name = widget_params[0]
            kwargs = widget_params[1]
            if len(widget_params)>2:
                kwargs['attrs'] = widget_params[2]
        if hasattr(widgets, widget_name):
            return getattr(widgets, widget_name)(**kwargs)
        elif widget_name in ['ProtoCheckboxSelectMultiple']:
            return ProtoCheckboxSelectMultiple(**kwargs)
        else:
            raise SchemaFormError, "Widget name '%s' for field '%s' does not exist in 'django.forms.widgets'" % (widget_name, widget_name)

    def get_form_display_sheme(self, step=1):
        """
        Renvoi le schéma de mise en forme du formulaire
        """
        scheme = getattr(self, 'form_display_scheme_step_%s'%step, None)
        if scheme:
            return dict(scheme)
        return None

    def get_all_shemes(self):
        """
        Renvoi le schéma de mise en forme du formulaire
        """
        shemes = []
        for attr in dir(self):
            if attr.startswith('form_display_scheme_step'):
                shemes = shemes + list(getattr(self, attr))

        return shemes

    def get_all_order(self):
        """
        Renvoi la liste complète de l'ordre d'affichage des champs
        """
        order = []
        for attr in dir(self):
            if attr.startswith('form_display_scheme_step'):
                order = order + [item[0] for item in getattr(self, attr)]

        return order
