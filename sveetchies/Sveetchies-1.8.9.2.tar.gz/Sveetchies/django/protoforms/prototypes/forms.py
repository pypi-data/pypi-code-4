# -*- coding: utf-8 -*-
from django import forms
from django.db import models
from django.contrib.localflavor.fr.forms import FRPhoneNumberField
from django.contrib.formtools.wizard import FormWizard
from django.contrib import messages
from django.core.validators import EMPTY_VALUES, MaxValueValidator
from django.template import loader as template_loader
from django.template import Context as template_Context

from Sveetchies.django.utils import get_metas

from Sveetchies.django.protoforms.models import SelectionValueExtension, SelectionItem

from Sveetchies.django.protoforms import PROTO_EXTENDED_VALUE_FIELD_KEY, PROTO_DATE_FIELD_FORMATS, PROTO_MESSAGE_FORM_SUCCESS, PROTO_SELECTION_KINDS
from Sveetchies.django.protoforms.prototypes.model_fields import ForeignKeySelectionModelField, ManyToManySelectionModelField, ProtoZipcodeModelField, ProtoPhoneModelField
from Sveetchies.django.protoforms.prototypes.form_fields import ProtoDateField, ProtoFRZipCodeField, ExtendedSelectionItemFormField, ForeignKeySelectionFormField, ManyToManySelectionFormField

class BaseForm(object):
    """
    Base la plus basse, inutilisable telle quelle car relie sur des attributs ou 
    méthodes de ses héritiers ciblés (Form et ModelForm)
    """
    def get_automatic_extension_fields(self):
        """
        Crée un registre de tuples (fieldname, extension_fieldname, value_key_to_extend) pour tout les champs 
        de séléction à étendre
        """
        self.cf_selection_extensions = []
        for k,v in self.fields.items():
            res = self.is_extension_formfield(k, v)
            if res:
                self.cf_selection_extensions.append(res)
    
    def is_extension_formfield(self, form_field_name, form_field_object):
        """
        Test qu'un champ de formulaire est une liste de séléction
        """
        extension_fieldname = PROTO_EXTENDED_VALUE_FIELD_KEY % form_field_name
        if isinstance(form_field_object, ForeignKeySelectionFormField) or isinstance(form_field_object, ManyToManySelectionFormField):
            try:
                ext = SelectionItem.objects.get(kind=form_field_object.collectorform_selectionitem_choices, value_extended=True)
            except SelectionItem.DoesNotExist:
                pass
            else:
                return form_field_name, extension_fieldname, ext.key
        return None
    
    def _cf_get_fields_order(self):
        """
        Retourne la liste d'ordre d'affichage des champs
        
        Cherche d'abord dans le ``Meta`` du ``Form`` si il possède bien un ``model`` et 
        un attribut ``cf_for_wizard_step`` qui définit l'indice de schéma à utiliser, 
        sinon fallback sur la liste automatique des champs faite par le ``Form``.
        """
        if hasattr(self, 'Meta'):
            if hasattr(self.Meta, 'model') and hasattr(self.Meta, 'cf_for_wizard_step'):
                field_list = self.Meta.model.objects.get_form_fields_order(step=self.Meta.cf_for_wizard_step)
                if field_list:
                    return field_list
        return self.fields.keys()
    cf_fields_order = property(_cf_get_fields_order)
    
    def _get_fields_scheme(self):
        """
        Retourne le schéma de mise en forme des champs
        
        Cherche d'abord dans le ``Meta`` du ``Form`` si il possède bien un ``model`` et 
        un attribut ``cf_for_wizard_step`` qui définit l'indice de schéma à utiliser, 
        sinon renvoi un simple `dict` vide.
        """
        if hasattr(self, 'Meta'):
            if hasattr(self.Meta, 'model') and hasattr(self.Meta, 'cf_for_wizard_step'):
                field_scheme = self.Meta.model.objects.get_form_display_sheme(step=self.Meta.cf_for_wizard_step)
                if field_scheme:
                    return field_scheme
        return {}
    cf_fields_scheme = property(_get_fields_scheme)

    def get_field_display_attrs(self, name, step=1):
        """
        Renvoi le schéma de mise en forme d'un champs particulier
        """
        sc = self.get_form_display_sheme(step=step)
        if sc:
            return sc.get(name, {}) 
            
        return {}
    
    def get_clean_model_fields(self):
        """
        Filtre les champs du modèles selon l'attribut d'exclusions du formulaire
        """
        fields = [item for item in self.Meta.model._meta.fields if item.name not in self.Meta.exclude]
        return fields
        
    def automatic_selectionitem_append(self):
        """
        Ajout/redéfinition automatique des champs de séléction  
        utilisant ``SelectionItem``
        """
        selections_labels = dict(PROTO_SELECTION_KINDS)
        # Introspection du modèle lié en Meta pour rechercher ses champs qui relie sur 
        # SelectionItem et les attribuer convenablement
        for item in self.get_clean_model_fields():
            if isinstance(item, ForeignKeySelectionModelField) or isinstance(item, ManyToManySelectionModelField):
                if item.name in self.fields:
                    fieldClass = ForeignKeySelectionFormField
                    if isinstance(item, ManyToManySelectionFormField):
                        fieldClass = ManyToManySelectionFormField
                    widget = forms.RadioSelect()
                    wparams = self.cf_fields_scheme[item.name]
                    if 'widget' in wparams:
                        widget = self.Meta.model.objects.get_widget_instance(wparams['widget'])
                    empty_label = wparams.get('empty_label', None)
                    self.fields[item.name] = fieldClass(
                        label=item.verbose_name,
                        selectionitem_choices=item.collectorform_selectionitem_kind,
                        widget=widget,
                        empty_label=empty_label,
                        required=not(item.blank)
                    )

    def automatic_field_changes(self):
        """
        Modification "communes" pour certains types de champs
        """
        for item in self.get_clean_model_fields():
            # Pour les champs de dates, mettre la syntaxe de la date "à la francaise"
            if isinstance(item, models.DateField):
                input_formats = PROTO_DATE_FIELD_FORMATS
                if item.name in self.cf_fields_scheme:
                    input_formats = self.cf_fields_scheme[item.name].get('input_formats', input_formats)
                self.fields[item.name] = ProtoDateField(
                    label=item.verbose_name,
                    required=not(item.blank),
                    input_formats=input_formats
                )
            # Pour les champs de code postaux on impose la syntaxe locale
            elif isinstance(item, ProtoZipcodeModelField):
                self.fields[item.name] = ProtoFRZipCodeField(
                    label=item.verbose_name,
                    required=not(item.blank),
                )
            elif isinstance(item, ProtoPhoneModelField):
                self.fields[item.name] = FRPhoneNumberField(
                    label=item.verbose_name,
                    required=not(item.blank),
                )
            elif not isinstance(item, ForeignKeySelectionModelField) and not isinstance(item, ManyToManySelectionModelField) and not isinstance(item, models.fields.AutoField):
                wparams = self.cf_fields_scheme[item.name]
                if 'widget' in wparams:
                    extra_kwargs = {}
                    if hasattr(item, 'choices'):
                        extra_kwargs['choices'] = item.choices
                    self.fields[item.name].widget = self.Meta.model.objects.get_widget_instance(wparams['widget'], kwargs=extra_kwargs)
    
    def automatic_extend_selectionitem_field(self):
        """
        Ajout automatique des champs de texte nécessaires aux valeurs de séléction à 
        étendre 
        """
        for fieldname, extension_fieldname, extension_key in self.cf_selection_extensions:
            self.fields[extension_fieldname] = ExtendedSelectionItemFormField(required=False, max_length=100)
    
    def automatic_fields_extracontext(self):
        """
        Ajout automatique du contexte optionnel sur mesure de mise en forme de chaque 
        champs
        """
        for k,v in self.fields.items():
            if k in self.cf_fields_scheme:
                v.cf_extracontext = self.cf_fields_scheme[k]
                continue
            v.cf_extracontext = {}
    
    def automatic_clean_extend(self):
        """
        Validation automatique des champs d'extension de séléction
        """
        cleaned_data = self.cleaned_data
        for fieldname, extension_fieldname, extension_key in self.cf_selection_extensions:
            selection_value = cleaned_data.get(fieldname)
            if selection_value and selection_value.key == extension_key:
                if cleaned_data.get(extension_fieldname) in EMPTY_VALUES:
                    self._errors[extension_fieldname] = self.error_class([u"Ce champ est obligatoire si vous séléctionnez la valeur '%s'"%selection_value.label])
        return cleaned_data
    
    def set_extend_selectionitem_fields(self, model_object, datas):
        """
        Ajoute automatiquement les valeurs des champs d'extensions dans un nouvel objet 
        du modèle ``SelectionValueExtension``
        """
        for fieldname, extension_fieldname, extension_key in self.cf_selection_extensions:
            if datas.get(extension_fieldname) not in EMPTY_VALUES:
                SelectionValueExtension(
                    content_object=model_object,
                    extended_field=fieldname,
                    value=datas.get(extension_fieldname),
                ).save()
    
    def post_save(self, model_object):
        """
        Traitements supplémentaires après la sauvegarde
        """
        metas = get_metas()
        
        self.send_emails(model_object, metas)
        self.transmit_success_message(model_object, metas)
    
    def send_emails(self, model_object, metas, **kwargs):
        """
        Envoi des emails suites à la sauvegarde des données du formulaires confirmé
        
        Méthode à implémenter dans l'héritage du Form pour y intégrer un traitement 
        d'envoi d'email après la sauvegarde d'une nouvelle entrée.
        """
        pass
    
    def transmit_success_message(self, model_object, metas, **kwargs):
        """
        Transmission des messages html à inclure dans la page de confirmation
        """
        if PROTO_MESSAGE_FORM_SUCCESS:
            d = {
                'metas': metas,
            }
            d.update(kwargs)
            html = template_loader.render_to_string('protoforms/cf_finish_message.html', template_Context(d))
            messages.add_message(self.requestObject, PROTO_MESSAGE_FORM_SUCCESS, html)
    
class BaseContainerForm(BaseForm, forms.Form):
    """
    Base d'un formulaire standard "manuel"
    
    Contrairement à un vrai ``Form`` "standard", il nécessite un Meta.model pour pouvoir 
    utiliser les schémas de mise en forme
    """
    def __init__(self, requestObject, *args, **kwargs):
        self.requestObject = requestObject
        super(BaseContainerForm, self).__init__(*args, **kwargs)
        # N'utilise pas ``automatic_selectionitem_append`` car ce type de formulaire 
        # définit tout ses champs manuellement
        self.get_automatic_extension_fields()
        self.automatic_extend_selectionitem_field()
        self.automatic_fields_extracontext()
    
    def clean(self):
        cleaned_data = self.automatic_clean_extend()
        return cleaned_data

    class Meta:
        # À écraser dans l'héritage par le modèle lié, nécessaire pour le système
        model = None

class BaseContainerModelForm(BaseForm, forms.ModelForm):
    """
    Base d'un formulaire construit depuis un modèle
    """
    def __init__(self, requestObject, *args, **kwargs):
        self.requestObject = requestObject
        super(BaseContainerModelForm, self).__init__(*args, **kwargs)
        self.automatic_selectionitem_append()
        self.get_automatic_extension_fields()
        self.automatic_field_changes()
        self.automatic_extend_selectionitem_field()
        self.automatic_fields_extracontext()
    
    def clean(self):
        cleaned_data = self.automatic_clean_extend()
        return cleaned_data

    class Meta:
        # À écraser dans l'héritage par le modèle lié, nécessaire pour le système
        model = None
