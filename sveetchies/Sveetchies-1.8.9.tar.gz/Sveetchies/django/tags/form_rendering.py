# -*- coding: utf-8 -*-
"""
Templates tags permettant une mise en forme des formulaires plus "stylisables" que les 
rendus par défaut fournit dans Django

Le code provient de protoforms à l'origine, mais séparé parce que ce dernier implémente 
aussi d'autres fonctionnalités inutile dans la plupart des cas habituels.

Le principe diverge un peu car le schéma des options de rendus des champs ne se trouvent 
plus dans le manager d'un modèle, mais est directement présent comme attribut 
"render_scheme" du formulaire.
"""
from django.conf import settings
from django import template
from django.utils.safestring import mark_safe
from django.forms.forms import BoundField
from django.utils.html import conditional_escape
from django.forms.util import flatatt

from Sveetchies.django.utils import get_string_or_variable

PROTOFORMS_FIELD_TEMPLATE = getattr(settings, 'PROTOFORMS_FIELD_TEMPLATE', "protoforms_field.html")

register = template.Library()

class ProtoBoundField(BoundField):
    """
    Extension pour un peu plus de finesse dans la conception du html d'un champ
    """
    def label_tag(self, contents=None, attrs=None, tag=None):
        """
        Wraps the given contents in a <label>, if the field has an ID attribute.
        Does not HTML-escape the contents. If contents aren't given, uses the
        field's HTML-escaped label.

        If attrs are given, they're used as HTML attributes on the <label> tag.
        """
        tag_attrs = None
        if tag and not isinstance(tag, basestring):
            tag, tag_attrs = tag
        contents = contents or conditional_escape(self.label)
        widget = self.field.widget
        id_ = widget.attrs.get('id') or self.auto_id
        if id_:
            attrs = attrs and flatatt(attrs) or ''
            if tag_attrs:
                attrs = attrs+" "+tag_attrs
            if tag is None:
                contents = u'<label for="{id_for}"{attrs}>{content}</label>'.format(id_for=widget.id_for_label(id_), attrs=attrs, content=unicode(contents))
            else:
                contents = u'<{tag}{attrs}>{content}</{tag}>'.format(tag=tag, attrs=attrs, content=unicode(contents))
        return mark_safe(contents)

@register.tag(name="form_render")
def do_form_render(parser, token):
    """
    Lecture de préparation du Tag *form_render*
    
    Affiche tout les champs disponible du formulaire selon ses options de rendus.
    
    Arguments :
    
    form_object
        Variable de l'objet du formulaire.
    field_template
        (optionnel) Chemin d'un template pour les champs
        
    Exemples d'utilisations dans un template : ::
    
        {% form_render form_object[ field_template] %}
    
    :type parser: object ``django.template.Parser``
    :param parser: Objet du parser de template.
    
    :type token: object ``django.template.Token``
    :param token: Objet de la chaîne découpée du tag capturé dans le template.
    
    :rtype: object ``FormTagRender``
    :return: L'objet du générateur de rendu du tag.
    """
    args = token.split_contents()
    if len(args) < 2:
        raise template.TemplateSyntaxError, "You need to specify at less a form object"
    else:
        return FormTagRender(*args[1:])

@register.tag(name="fieldset_render")
def do_fieldset_render(parser, token):
    """
    Lecture de préparation du Tag *fieldset_render*
    
    Affiche seulement les champs spécifiés selon ses options de rendus. Cela permet de 
    faire des groupements séparés de champs avec un même controleur de formulaire.
    
    Arguments :
    
    form_object
        Variable de l'objet du formulaire.
    fields
        Liste des noms de champs à afficher, séparés par des virgules sans espaces.
    field_template
        (optionnel) Chemin d'un template pour les champs
        
    Exemples d'utilisations dans un template : ::
    
        {% fieldset_render form_object "field1,field2,etc"[ field_template] %}
    
    :type parser: object ``django.template.Parser``
    :param parser: Objet du parser de template.
    
    :type token: object ``django.template.Token``
    :param token: Objet de la chaîne découpée du tag capturé dans le template.
    
    :rtype: object ``FormTagRender``
    :return: L'objet du générateur de rendu du tag.
    """
    args = token.split_contents()
    if len(args) < 2:
        raise template.TemplateSyntaxError, "You need to specify a form object"
    elif len(args) < 3:
        raise template.TemplateSyntaxError, "You need to specify a fieldset"
    elif len(args) == 3:
        return FormTagRender(args[1], fieldset=args[2])
    else:
        return FormTagRender(args[1], field_template_varname=args[3], fieldset=args[2])

class FormTagRender(template.Node):
    """
    Génération du html d'un formulaire selon ses options de rendu
    """
    def __init__(self, form_object_varname, field_template_varname=None, fieldset=None):
        """
        :type form_object_varname: string or object ``django.forms.Form``
        :param form_object_varname: Nom de variable de l'objet du formulaire ou 
                                    directement l'objet.
        """
        self.form_object_varname = form_object_varname
        self.field_template_varname = field_template_varname
        self.fieldset = fieldset
    
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
        # Résolution de l'instance du formulaire
        self.form_object = get_string_or_variable(self.form_object_varname, context)
        # Résolution du chemin de template
        self.field_template = PROTOFORMS_FIELD_TEMPLATE
        if self.field_template_varname:
            self.field_template = get_string_or_variable(self.field_template_varname, context)
        # Mise en place des options de rendu
        self._fields_scheme = {
            'order': None,
            'drop_helps': (),
            'fields': {
                #'EXAMPLE': {
                    #"container_id": "mon_conteneur_unique_de_champ",
                    #"label": u"Etes-vous humain&#160;?",
                    #"label_tag": "h4",
                    #"label_tag": ('h4', 'class="..."'),
                    #"label_suffix": False, # désactive le suffix de label tel que ":"
                    #"widget": "RadioSelect",
                    #"extra_class": ["flat_choices"],
                    #'help_text': 'Année au format AAAA',
                    #'input_formats': ('%Y',), # utile seulement pour un widget de date (?)
                #},
            },
        }
        self._fields_scheme.update(getattr(self.form_object, 'render_scheme', {'fields': {}}))
        
        # Liste ordonnée des noms des champs à traiter
        # Liste de champs directement par le tag
        if self.fieldset:
            self._fields_order = get_string_or_variable(self.fieldset, context).split(',')
        else:
            # Liste par défaut récupéré dans l'instance du formulaire
            self._fields_order = self.form_object.fields.keys()
            # Liste définie dans les options de rendus
            if self._fields_scheme.get('order', None):
                self._fields_order = self._fields_scheme['order']
        
        # Parcours des champs à concevoir
        for i, k in enumerate(self._fields_order):
            if k in self.form_object.fields:
                v = self.form_object.fields[k]
                # Conception du html de l'élément
                html += self.get_field_container(k, v, first=not(i > 0), last=((i+1)>=len(self._fields_order)))
        
        return html
    
    def get_field_container(self, fieldname, field_object, first=False, last=False):
        """
        Génère et renvoi le rendu html d'un champ
        """
        default_class = ['formItem']
        css_classes = []
        
        # Flag css du premier élément
        if first:
            default_class.append('first-formItem')
        # Flag css du dernier élément si il n'a pas d'extension, auquel le flag est 
        # transféré à ce dernier
        if last:
            default_class.append('last-formItem')

        # Éléments du conteneur
        attrs = {'default_class':default_class, 'css_classes':css_classes}
        
        # Contexte du template
        context = self.get_field_html_context(fieldname, field_object, attrs)
        if isinstance(context, basestring):
            return context
        
        # Rendu dans son template
        html = template.loader.render_to_string(self.field_template, context)
        
        return html
    
    def get_field_label(self, fieldname, field_object, render_opts, bf):
        """
        Détermine le label à afficher
        """
        label = bf.field.label
        if label is None:
            if hasattr(self.form_object, '_meta'):
                field_model = getattr(self.form_object._meta.model, fieldname, None)
                if field_model:
                    label = getattr(field_model.field, 'verbose_name')
        
        if label is not None:
            label = unicode(label)
        
        if 'label' in render_opts:
            return render_opts['label']
        
        return label
    
    def get_field_html_context(self, fieldname, field_object, attrs):
        """
        Construit le context de template du champ
        """
        render_opts = self._fields_scheme['fields'].get(fieldname, {})
        # Calcul des éléments lié à l'input (champs, label, id, etc..)
        bf = ProtoBoundField(self.form_object, field_object, fieldname)
        id_ = bf.field.widget.attrs.get('id') or bf.auto_id
        label = self.get_field_label(fieldname, field_object, render_opts, bf)
        field_id = bf.field.widget.id_for_label(id_)
        field_type = str(field_object.__class__)[8:-2].split(".")[-1].lower()
        attrs['css_classes'].append("container_field_%s"%field_type)
        
        # Récupère le nom de class du widget du champ et s'en sert comme class 
        # css <class 'django.forms.widgets.Machin'>
        widget_type = str(bf.field.widget.__class__)[8:-2].split(".")[-1].lower()
        attrs['css_classes'].append("container_widget_%s"%widget_type)
        
        # Pas besoin d'aller plus loin pour les champs cachés, on retourne directement leur <input/>
        if widget_type in ('hiddeninput', 'multiplehiddeninput', 'inlineforeignkeyhiddeninput'):
            return bf.as_widget()
        
        # Aide récupérée du modèle
        help_text = None
        if fieldname not in self._fields_scheme['drop_helps']:
            if 'help_text' in render_opts:
                if render_opts.get('help_text', None):
                    help_text = mark_safe(render_opts['help_text'])
            elif hasattr(field_object, "help_text"):
                help_text = mark_safe(field_object.help_text)
        
        # Dictionnaire du contexte
        d = {
            "name": fieldname,
            "attrs": attrs,
            "field_id": field_id,
            "field_type": field_type,
            "container_id": "container_%s" % field_id,
            "label": label,
            "label_tag": bf.label_tag(contents=self.format_label_content(fieldname, field_object, render_opts, widget_type, label), attrs={'class':"labeltitle"}, tag=render_opts.get('label_tag', None)),
            "field": bf.as_widget(),
            "errors": bf.errors,
            "required": bf.field.required,
            "widget_type": widget_type,
            "help": help_text,
        }
        # Rédéfinition selon les attributs optionnels dans le schéma de mise en 
        # forme (du manager)
        if 'extra_class' in render_opts:
            classes = d['attrs']['css_classes']
            d['attrs']['css_classes'] = classes+[item for item in render_opts['extra_class'] if item not in classes]
        if 'container_id' in render_opts:
            d['container_id'] = render_opts['container_id']
            
        d['attrs'] = self.get_css_classes_html(**attrs)
        
        return template.Context(d)
    
    def format_label_content(self, fieldname, field_object, render_opts, widget_type, content):
        """
        Formate le label du champ
        """
        if content == None:
            content = fieldname
        context = {
            "content": content,
            "required": '',
            "suffix": '',
        }
        # Ajout du suffixe sauf pour les "checkboxinput" qui ont une disposition 
        # particulière (input+label)
        suffix = ''
        if widget_type != "checkboxinput":
            suffix = self.label_suffix
            if 'label_suffix' in render_opts:
                suffix = render_opts['label_suffix']
            if not isinstance(suffix, basestring):
                suffix = ''
            if content[-1] not in self.label_protected_ends:
                context['suffix'] = '&#160;'+suffix
            # Marqueur de champ obligatoire
            if field_object.required:
                context['required'] = '&#160;'+self.label_required
        
        content = u'{content}{required}{suffix}'.format(**context)
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
