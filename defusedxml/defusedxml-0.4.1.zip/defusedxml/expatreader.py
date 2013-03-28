# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See http://www.python.org/psf/license for licensing details.
"""Defused xml.sax.expatreader
"""
from __future__ import print_function, absolute_import

from xml.sax.expatreader import ExpatParser as _ExpatParser

from .common import (DTDForbidden, EntitiesForbidden,
                     ExternalReferenceForbidden)

__origin__ = "xml.sax.expatreader"


class DefusedExpatParser(_ExpatParser):
    """Defused SAX driver for the pyexpat C module."""

    def __init__(self, namespaceHandling=0, bufsize=2 ** 16 - 20,
                 forbid_dtd=False, forbid_entities=True,
                 forbid_external=True):
        _ExpatParser.__init__(self, namespaceHandling, bufsize)
        self.forbid_dtd = forbid_dtd
        self.forbid_entities = forbid_entities
        self.forbid_external = forbid_external

    def defused_start_doctype_decl(self, name, sysid, pubid,
                                   has_internal_subset):
        raise DTDForbidden(name, sysid, pubid)

    def defused_entity_decl(self, name, is_parameter_entity, value, base,
                            sysid, pubid, notation_name):
        raise EntitiesForbidden(name, value, base, sysid, pubid, notation_name)

    def defused_unparsed_entity_decl(self, name, base, sysid, pubid,
                                     notation_name):
        # expat 1.2
        raise EntitiesForbidden(name, None, base, sysid, pubid, notation_name)

    def defused_external_entity_ref_handler(self, context, base, sysid,
                                            pubid):
        raise ExternalReferenceForbidden(context, base, sysid, pubid)

    def reset(self):
        _ExpatParser.reset(self)
        parser = self._parser
        if self.forbid_dtd:
            parser.StartDoctypeDeclHandler = self.defused_start_doctype_decl
        if self.forbid_entities:
            parser.EntityDeclHandler = self.defused_entity_decl
            parser.UnparsedEntityDeclHandler = self.defused_unparsed_entity_decl
        if self.forbid_external:
            parser.ExternalEntityRefHandler = self.defused_external_entity_ref_handler


def create_parser(*args, **kwargs):
    return DefusedExpatParser(*args, **kwargs)
