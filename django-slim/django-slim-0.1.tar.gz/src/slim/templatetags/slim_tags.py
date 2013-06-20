__title__ = 'slim.templatetags.slim_tags'
__version__ = '0.1'
__build__ = 0x000001
__author__ = 'Artur Barseghyan <artur.barseghyan@gmail.com>'
__all__ = ('get_translated_object_for', 'get_translated_objects_for', 'set_language', 'get_language_name_by_key', \
           'multiling_is_enabled')

import re

from django.utils.translation import ugettext_lazy as _
from django import template
from django.template import Library
from django.utils import translation

from slim.helpers import smart_resolve, default_language, get_language_from_request, get_languages_keys

register = Library()


class GetTranslatedObjectForNode(template.Node):
    """
    Node for template tag ``get_translated_object_for``.
    """
    def __init__(self, obj, as_var, language=None):
        """
        :param obj: Object to translate.
        :param string as_var: Desired variable name in the template context.
        :param str language: Language code. Must be one of those defined in ``LANGUAGES``
            of "settigns.py"
        :raise template.TemplateSyntaxError: If invalid syntax or in case if HttpRequest
            can't be retrieved from template context, while ``language`` attribute is not
            specified.
        """
        self.as_var = as_var
        self.obj = obj
        self.language = language

    def render(self, context):
        ret_val = None
        obj = smart_resolve(self.obj, context)

        try:
            is_multilingual = obj.is_multilingual
        except AttributeError, e:
            is_multilingual = False
            raise template.TemplateSyntaxError(
                _("Invalid usage of ``get_translated_object_for``. Translated object shall be multilingual.")
                )

        try:
            request = context['request']
        except:
            request = None

        if language is None and request is None:
            raise template.TemplateSyntaxError(
                _("Invalid usage of ``get_translated_object_for``. Can't retrieve ``HttpRequest`` object from "
                   "template context, while ``language`` attribute is not specified.")
                )

        if language is None:
            language = get_language_from_request(request)
        else:
            language = smart_resolve(self.language, context)
            if language:
                language = str(language)
            else:
                language = default_language

        ret_val = obj.get_translation_for(language)

        if self.as_var:
            context[self.as_var] = ret_val
            return ''
        return ret_val


@register.tag
def get_translated_object_for(parser, token):
    """
    Gets translated object for the object given.

    Syntax::
        {% get_translated_object_for [object] language=[language] as [var_name] %}

    Example usage::
        {% get_translated_object_for article as translated_article %}
        {% get_translated_object_for article language=ru as translated_article %}
    """
    bits = token.contents.split()
    if 'as' != bits[-2]:
        raise template.TemplateSyntaxError(
            _("Invalid syntax for %s. You must specify a name for translated object." % bits[0])
            )
    as_var = bits[-1]
    try:
        obj = parser.compile_filter(bits[1])
    except:
        template.TemplateSyntaxError(_("Invalid syntax for %s. You must provide an object to translate." % bits[0]))

    m = re.search(r'language=(\w+)', ' '.join(bits[2:-2]))

    if m:
        language = parser.compile_filter(m.groups()[0])
    else:
        language = None

    return GetTranslatedObjectForNode(obj=obj, as_var=as_var, language=language)


class GetTranslatedObjectsForNode(template.Node):
    """
    Node for template tag ``get_translated_objects_for``.
    """
    def __init__(self, obj, as_var):
        """
        :param obj: Object to get translations for.
        :param str as_var: Desired variable name in the template context.
        :raise template.TemplateSyntaxError: If invalid syntax or in case if HttpRequest
            can't be retrieved from template context, while ``language`` attribute is not
            specified.
        """
        self.as_var = as_var
        self.obj = obj

    def render(self, context):
        ret_val = None
        obj = smart_resolve(self.obj, context)

        try:
            is_multilingual = obj.is_multilingual
        except AttributeError, e:
            is_multilingual = False
            raise template.TemplateSyntaxError(
                _("Invalid usage of get_translated_object_for. Translated object shall be multilingual.")
                )

        ret_val = obj.available_translations()

        if self.as_var:
            context[self.as_var] = ret_val
            return ''
        return ret_val


@register.tag
def get_translated_objects_for(parser, token):
    """
    Gets translations available for the given object.

    Syntax::
        {% get_translated_objects_for [object] as [var_name] %}

    Example usage::
        {% get_translated_objects_for article as translated_article %}
    """
    bits = token.contents.split()
    if 'as' != bits[-2]:
        raise template.TemplateSyntaxError(
            _("Invalid syntax for %s. You must specify a name for translated object." % bits[0])
            )
    as_var = bits[-1]
    try:
        obj = parser.compile_filter(bits[1])
    except:
        template.TemplateSyntaxError(_("Invalid syntax for %s. You must provide an object to translate." % bits[0]))

    return GetTranslatedObjectsForNode(obj=obj, as_var=as_var)


class SetLanguageNode(template.Node):
    """
    Node for ``set_language`` tag.
    """
    def __init__(self, language=None):
        self.language = language

    def render(self, context):
        # Try to get request.LANGUAGE_CODE. If fail, use default one.
        request = context['request']
        language = get_language_from_request(request, default=None)

        if not language:
            language = smart_resolve(self.language, context)
            if not language in get_languages_keys():
                language = default_language

        translation.activate(language)
        return ''


@register.tag
def set_language(parser, token):
    """
    Sets current language code.

    FIXME: This is actually a hack.

    Syntax::
        {% set_language [language] %}
    Example::
        {% set_language ru %}
    """
    bits = token.contents.split()
    if 2 < len(bits):
        raise template.TemplateSyntaxError("'%s' tag takes one argument at most" % bits[0])
    elif 2 == len(bits):
        language = parser.compile_filter(bits[1])
    else:
        language = None
    return SetLanguageNode(language=language)


class GetLanguageNameByKeyNode(template.Node):
    """
    Node for ``get_language_name_by_key`` tag.
    """
    def __init__(self, key, as_var=None, translate=False):
        self.key = key
        self.as_var = as_var
        self.translate = translate

    def render(self, context):
        # Try to get request.LANGUAGE_CODE. If fail, use default one.
        key = smart_resolve(self.key, context)
        translate = smart_resolve(self.translate, context)
        languages = dict(get_languages())

        if languages.has_key(key):
            ret_val = languages[key]
        else:
            ret_val = None

        if translate:
            ret_val = ugettext(ret_val)

        if self.as_var:
            context[self.as_var] = ret_val
            return ''
        return ret_val


@register.tag
def get_language_name_by_key(parser, token):
    """
    Gets language name by key given

    FIXME: This is actually a hack.

    Syntax::
        {% get_language_name_by_key [key] [translate] as [var_name] %}
    Example::
        {% get_language_name_by_key ru translate as language_key %}
    """
    bits = token.contents.split()
    if 5 < len(bits):
        raise template.TemplateSyntaxError("'%s' tag takes five arguments at most" % bits[0])

    key = parser.compile_filter(bits[1])

    m = re.search(r'translate=(\d)', ' '.join(bits[2:-2]))

    if m:
        translate = parser.compile_filter(m.groups()[0])
    else:
        translate = None

    if 'as' != bits[-2]:
        raise template.TemplateSyntaxError(
            _("Invalid syntax for %s. You must specify a name for translated object." % bits[0])
            )
    as_var = bits[-1]

    return GetLanguageNameByKeyNode(key=key, as_var=as_var, translate=translate)


class MultilinIsEnabledNode(template.Node):
    """
    Node for ``multiling_is_enabled`` tag.
    """
    def __init__(self, as_var=None):
        self.as_var = as_var

    def render(self, context):
        # Try to get request.LANGUAGE_CODE. If fail, use default one.
        if len(get_languages_keys()) > 1:
            ret_val = True
        else:
            ret_val = False

        if self.as_var:
            context[self.as_var] = ret_val
            return ''
        return ret_val


@register.tag
def multiling_is_enabled(parser, token):
    """
    Checks if multiling shall be enabled (in templates). Simply, if LANGUAGES tuple contains more than one
    language, we return boolean True; otherwise - boolean False.

    Syntax::
        {% multiling_is_enabled as [var_name] %}
    Example::
        {% multiling_is_enabled as multiling_is_enabled %}
    """
    bits = token.contents.split()
    if not len(bits) in (1, 3):
        raise template.TemplateSyntaxError("'%s' tag takes five arguments at most" % bits[0])

    if 3 == len(bits):
        if 'as' != bits[-2]:
            raise template.TemplateSyntaxError(
                _("Invalid syntax for %s. You must specify a name for translated object." % bits[0])
                )
        as_var = bits[-1]
    else:
        as_var = None

    return MultilinIsEnabledNode(as_var=as_var)
