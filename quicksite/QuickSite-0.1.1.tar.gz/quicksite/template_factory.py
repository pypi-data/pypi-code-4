""" Factory object for template generators
"""

__author__ = "Russell Hay"

import logging
log = logging.getLogger(__name__)

from quicksite.simple_template import SimpleTemplate

TEMPLATE_REGISTRY = { }

def register_template(type_, me):
    global TEMPLATE_REGISTRY
    TEMPLATE_REGISTRY[type_] = me

def template(source, definition):
    global TEMPLATE_REGISTRY
    if hasattr(definition, "keys") and "type" in definition:
        if definition['type'] in TEMPLATE_REGISTRY:
            return TEMPLATE_REGISTRY[definition['type']](source, definition)
        else:
            raise TemplateTypeNotFound(definition['type'])
    else:
        return SimpleTemplate(source, definition)

class TemplateTypeNotFound(Exception):
    """ The template type specified "{type_}" was not found """
    def __init__(self, type_):
        super(TemplateTypeNotFound, self).__init__(self.__doc__.format(type_=type_))