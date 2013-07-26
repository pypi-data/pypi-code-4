# -*- coding: utf-8 -*-
"""
Templates tags
"""
from string import Template as StringTemplate

from django.conf import settings
from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.forms.forms import BoundField

from Sveetchies.django.utils import get_string_or_variable

from Sveetchies.django.protoforms import PROTO_EXTENDED_VALUE_FIELD_KEY, PROTO_FIELD_TEMPLATE
from Sveetchies.django.protoforms.prototypes.form_fields import ForeignKeySelectionFormField

register = template.Library()

@register.tag(name="form_render")
def do_form_render(parser, token):
    """
    Lecture de préparation du Tag *form_render*
    
    Arguments :
    
    form_object
        Variable de l'objet du formulaire.
    field_template
        (optionnel) Chemin d'un template pour les champs
        
    Exemples d'utilisations dans un template : ::
    
        {% form_render form_object field_template %}
    
    :type parser: object ``django.template.Parser``
    :param parser: Objet du parser de template.
    
    :type token: object ``django.template.Token``
    :param token: Objet de la chaîne découpée du tag capturé dans le template.
    
    :rtype: object ``FormTagRender``
    :return: L'objet du générateur de rendu du tag.
    """
    args = token.split_contents()
    if args < 2:
        raise template.TemplateSyntaxError, "You need to specify at less a form object"
    else:
        return FormTagRender(*args[1:])

class FormTagRender(template.Node):
    """
    Génération du rendu html du tag *cell_render*
    """
    def __init__(self, form_object_varname, field_template_varname=None):
        """
        :type form_object_varname: string or object ``django.forms.Form``
        :param form_object_varname: Nom de variable de l'objet du formulaire ou 
                                    directement l'objet.
        """
        self.form_object_varname = form_object_varname
        self.field_template_varname = field_template_varname
    
    def render(self, context):
        """
        Rendu de tout les éléments du formulaire indiqué
        
        :type context: object ``django.template.Context``
        :param context: Objet du contexte du tag.
        
        :rtype: string
        :return: Le rendu généré pour le tag capturé.
        """
        html = ''
        self.label_protected_ends = (':', '?', '.', ',')
        self.label_suffix = ':'
        self.label_required = '<span class="required_tag">*</span>'
        self.label_content_template = '${content}${required}${suffix}'
        # Résolution de la variable dans le contexte
        self.form_object = get_string_or_variable(self.form_object_varname, context)
        self._order_fields = getattr(self.form_object, "cf_fields_order", self.form_object.fields.keys())
        print self.form_object.fields.keys()        
        
        self.field_template = PROTO_FIELD_TEMPLATE
        if self.field_template_varname:
            self.field_template = get_string_or_variable(self.field_template_varname, context)
        
        i = 0
        for k in self._order_fields:
            if k not in self.form_object.fields:
                raise template.VariableDoesNotExist("Failed lookup for key scheme [%s] in fields", (k,))
            v = self.form_object.fields[k]
            if not hasattr(v, "cf_extracontext"):
                v.cf_extracontext = {}
            html += self.get_field_container(k, v, first=not(i > 0), last=((i+1) >= len(self._order_fields)))
            i += 1
        
        return html
    
    def get_field_container(self, fieldname, field_object, first=False, last=False):
        """
        Génère et renvoi le rendu html d'un champ
        """
        default_class = ['formItem']
        css_classes = []
        to_extend_to = False
        
        # Recherche d'un champ automatique d'extension
        if isinstance(field_object, ForeignKeySelectionFormField):
            extension_fieldname = PROTO_EXTENDED_VALUE_FIELD_KEY % fieldname
            # Si le champs existe dans l'objet de formulaire et qu'il n'est pas déja 
            # dans la liste d'ordre d'affichage, on le rajoute à la suite
            if extension_fieldname in self.form_object.fields and extension_fieldname not in self._order_fields:
                to_extend_to = extension_fieldname
        
        # Flag css du premier élément
        if first:
            default_class.append('first-formItem')
        # Flag css du dernier élément si il n'a pas d'extension, auquel le flag est 
        # transféré à ce dernier
        if last and not to_extend_to:
            default_class.append('last-formItem')

        # Éléments du conteneur
        attrs = {'default_class':default_class, 'css_classes':css_classes}
        
        # Contexte du template
        html = template.loader.render_to_string(self.field_template, self.get_field_html_context(fieldname, field_object, attrs))
        
        # Insère le champ automatique d'extension juste à la suite
        if to_extend_to:
            html += self.get_field_container(to_extend_to, self.form_object.fields[to_extend_to], last=last)
        
        return html
    
    def get_field_label(self, fieldname, field_object, bf):
        """
        Détermine le label à afficher
        """
        label = bf.field.label
        if label is None:
            field_model = getattr(self.form_object._meta.model, fieldname, None)
            if field_model:
                label = getattr(field_model.field, 'verbose_name')
        
        if label is not None:
            label = unicode(label)
        
        if 'label' in field_object.cf_extracontext:
            if field_object.cf_extracontext['label']:
                return field_object.cf_extracontext['label']
            else:
                return None
        
        return label
    
    def get_field_html_context(self, fieldname, field_object, attrs):
        """
        Construit le context de template du champ
        """
        # Calcul des éléments lié à l'input (champs, label, id, etc..)
        bf = BoundField(self.form_object, field_object, fieldname)
        id_ = bf.field.widget.attrs.get('id') or bf.auto_id
        label = self.get_field_label(fieldname, field_object, bf)
        field_id = bf.field.widget.id_for_label(id_)
        field_type = str(field_object.__class__)[8:-2].split(".")[-1].lower()
        attrs['css_classes'].append("container_field_%s"%field_type)
        
        # Récupère le nom de class du widget du champ et s'en sert comme class 
        # css <class 'django.forms.widgets.Machin'>
        widget_type = str(bf.field.widget.__class__)[8:-2].split(".")[-1].lower()
        attrs['css_classes'].append("container_widget_%s"%widget_type)
        
        # Aide récupérée du modèle
        # TODO: une option (global?) pour ne pas les utiliser
        dropped_helps = getattr(self.form_object.Meta, 'protoforms_drop_helps', [])
        help_text = None
        if fieldname not in dropped_helps and hasattr(field_object, "help_text"):
            help_text = field_object.help_text
        
        # Dictionnaire du contexte
        d = {
            "name": fieldname,
            "attrs": attrs,
            "field_id": field_id,
            "field_type": field_type,
            "container_id": "container_%s" % field_id,
            "label": label,
            "label_tag": bf.label_tag(contents=self.format_label_content(fieldname, field_object, widget_type, label), attrs={'class':"labeltitle"}),
            "field": bf.as_widget(),
            "errors": bf.errors,
            "required": bf.field.required,
            "widget_type": widget_type,
            "help": help_text,
        }
        # Rédéfinition selon les attributs optionnels dans le schéma de mise en 
        # forme (du manager)
        if 'extra_class' in field_object.cf_extracontext:
            classes = d['attrs']['css_classes']
            d['attrs']['css_classes'] = classes+[item for item in field_object.cf_extracontext['extra_class'] if item not in classes]
        if 'container_id' in field_object.cf_extracontext:
            d['container_id'] = field_object.cf_extracontext['container_id']
        if 'help' in field_object.cf_extracontext:
            d['help'] = field_object.cf_extracontext['help']
            
        d['attrs'] = self.get_css_classes_html(**attrs)
        
        return template.Context(d)
    
    def format_label_content(self, fieldname, field_object, widget_type, content):
        """
        Formate le label du champ
        """
        if content == None:
            content = fieldname
        d = {
            "content": content,
            "required": '',
            "suffix": '',
        }
        # Ajout du suffixe sauf pour les "checkboxinput" qui ont une disposition 
        # particulière (input+label)
        suffix = ''
        if widget_type != "checkboxinput":
            suffix = self.label_suffix
            if 'label_suffix' in field_object.cf_extracontext:
                suffix = field_object.cf_extracontext['label_suffix']
            if not isinstance(suffix, basestring):
                suffix = ''
            if content[-1] not in self.label_protected_ends:
                d['suffix'] = '&#160;'+suffix
            # Marqueur de champ obligatoire
            if field_object.required:
                d['required'] = '&#160;'+self.label_required
        
        content = StringTemplate(self.label_content_template).safe_substitute(d)
        return mark_safe(template.defaultfilters.capfirst(content))
    
    def get_css_classes_html(self, default_class=None, css_classes=None):
        """
        Renvoi l'attribut HTML des classes CSS si il y'en a
        
        :type default_class: list
        :param default_class: (optional) Classe CSS par défaut.
        
        :type css_classes: list
        :param css_classes: (optional) Liste de classes CSS à ajouter en plus de celle 
                            par défaut.
        
        :rtype: string
        :return: L'attribut HTML des class CSS si il y'en a, sinon une chaine vide.
        """
        if not default_class and not css_classes:
            return ''
        
        if not default_class:
            default_class = []
        if not css_classes:
            css_classes = []
        
        if default_class and default_class not in css_classes:
            css_classes = default_class+[i for i in css_classes if i not in default_class]

        return mark_safe(' class="%s"' % ' '.join(css_classes))
