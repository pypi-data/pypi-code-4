#-*- coding: utf-8 -*-
# copyright 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr/ -- mailto:contact@logilab.fr
#
# This file is part of CubicWeb.
#
# CubicWeb is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# CubicWeb is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with CubicWeb.  If not, see <http://www.gnu.org/licenses/>.
from yams.xy import XYRegistry, UnsupportedVocabulary
from yams.constraints import SizeConstraint

from cubicweb.schema import VIRTUAL_RTYPES

from cubes.dataio.interfaces import (DEFAULT_CONVERTERS, DEFAULT_NAMESPACE,
                                     NAMESPACES, normalize_xml)

_ = unicode


SKIP_RTYPES = VIRTUAL_RTYPES | set(['cwuri', 'is', 'is_instance_of'])
META_ATTRIBUTES = ('eid', 'modification_date', 'creation_date')


###############################################################################
###############################################################################
###############################################################################
###  !!!! WARNING !!!!  #######################################################
### This code is fow now experimental, and should be used wisely. #############
###############################################################################
###############################################################################
###############################################################################


###############################################################################
### RDF XY CONFIGURATION ######################################################
###############################################################################
# XXX  Perhaps this may be used as a RDFCFG (similar to uicfg)
class DataioXY(XYRegistry):

    def __init__(self):
        """ An RDF configuration object based on the XYRegistry of Yams.

        Parameters:
           - concatenation_str: string used for concatenation of multiples attributes
                                if required.
           - allow_multiple_values: allow multiple values for a property
                                    (i.e. concatenate them).
        """
        super(DataioXY, self).__init__()
        self.concatenation_str = None
        self.allow_multiple_values = True
        # Namespaces
        self.namespaces = {}
        self.reverse_namespaces = {}
        for prefix, xmlns in NAMESPACES.items():
            self.register_prefix(prefix, xmlns)
        # Push
        # Rdf property used for etype guessing
        self.rdf_etype_property = 'rdf:type'
        # Uri conversion callback
        self.uri_conversion_callback = None
        # Callback for etype guessing
        self.etype_callback = None
        # Add converters callbacks
        self.attributes_callbacks = dict(DEFAULT_CONVERTERS)
        self.relations_callbacks = {}
        self.relations_etype_callbacks = {}
        # Dictionnary to store the different attributes
        # for a given etype
        self.attributes_by_etype = {}
        self.inlined_relations_by_etype = {}
        # Mapping between RDF and etype
        self.rdf2etype = {}
        # Base uri
        self.base_uri = None
        self.externaluri_callback = None
        # Schema
        self.attributes_by_etype = {}
        self.inlined_relations_by_etype = {}


    ###########################################################################
    ### XML/YAMS MAPPING HANDLING #############################################
    ###########################################################################
    def add_equivalence(self, yamssnippet, xmlsnippet):
        """ Add an equivalence between a yams snippet and an xml snippet
        """
        ykey = self._norm_yams_key(yamssnippet)
        # Check if the yams snippet is about an entity, i.e. only one string
        isentity = not isinstance(ykey, tuple)
        xkey = self._norm_xml_key(xmlsnippet, isentity=isentity)
        self._y2x.setdefault(ykey, []).append(xkey)
        # For relation (i.e. triples), we should "normalize" the object
        # in order to correctly retrieve for RDF view
        if len(yamssnippet.split(' ')) == 3:
            yamssnippet = yamssnippet.split(' ')
            yamssnippet[2] = '*'
            self._y2x.setdefault(' '.join(yamssnippet), []).append(xkey)
        self._x2y.setdefault(xkey, []).append(ykey)
        if not isentity:
            for dict, key, value in ((self._x2y, xkey, ykey),
                                     (self._y2x, ykey, xkey)):
                if key[0] != '*':
                    wkey = ('*',) + key[1:]
                    dict.setdefault(wkey, []).append(value)
                if key[2] != '*':
                    wkey = key[:2] + ('*',)
                    dict.setdefault(wkey, []).append(value)
        elif isentity and len(xkey)>1:
            # Complexe etype conversion
            self.rdf2etype[ykey] = xkey

    def yeq(self, xmlsnippet, isentity=False):
        """ Redefine XY.yeq to deals with 'rdfvocab:*' xml snippet
        """
        key = self._norm_xml_key(xmlsnippet, isentity)
        if not key:
            return
        try:
            return self._x2y[key]
        except KeyError:
            pass
        try:
            key = list(key)
            key[1] = (key[1][0], '*')
            return self._x2y[tuple(key)]
        except KeyError:
            raise UnsupportedVocabulary(key)

    def _norm_xml_key(self, xmlsnippet, isentity=False):
        """ Normalize an XML key """
        parts = []
        for xmlsnippet in xmlsnippet.split(' '):
            if ':' not in xmlsnippet:
                return
            pfx, tag = xmlsnippet.rsplit(':', 1)
            xmlns = self.prefixes.get(pfx, pfx)
            parts.append( (xmlns, tag) )
        if isentity:
            # Mutiple parts possible for complex etype conversion
            return tuple(parts)
        if len(parts) == 1:
            return '*', parts[0], '*'
        if len(parts) == 2:
            parts.append('*')
        assert len(parts) == 3
        return tuple(parts)

    def _xeq(self, yamssnippet):
        """ Equivalent version of yams.xeq without the normalization
        """
        try:
            return self._y2x[yamssnippet]
        except KeyError:
            raise UnsupportedVocabulary(yamssnippet)

    def xeq(self, yamssnippet):
        """ More generic version of xeq tha may deal with '* attr' rules
        """
        key = self._norm_yams_key(yamssnippet)
        try:
            # Try first etype-specific rule
            return self._xeq(key)
        except UnsupportedVocabulary:
            # Try rule available for all etypes,
            # i.e. rule like "* <attribute name>'
            try:
                key = list(key)
                key[0] = '*'
                return self._xeq(tuple(key))
            except UnsupportedVocabulary:
                return []
        return []


    ###########################################################################
    ### URI HANDLING ##########################################################
    ###########################################################################
    def normalize_uri(self, uri):
        """ Normalize the uri if required, e.g.:
        http://data.nytimes.com/XXX.rdf -> http://data.nytimes.com/XXX
        """
        if self.uri_conversion_callback:
            return self.uri_conversion_callback(uri)
        return uri

    def merge_uri_dictionnary(self, uri_dictionnary):
        """ This function normalize the uris (i.e. the keys)
        of the uri dictionnary given and merge the, now possible,
        identical entries. """
        new_uri_dictionnary = {}
        for uri, rdf_properties in uri_dictionnary.iteritems():
            uri = self.normalize_uri(uri)
            actual_dict = new_uri_dictionnary.get(uri, {})
            for rdf_prop, values in rdf_properties.iteritems():
                actual_dict.setdefault(rdf_prop, []).extend(values)
            new_uri_dictionnary[uri] = actual_dict
        return new_uri_dictionnary

    def add_to_existing_uri_dictionnary(self, uri, rdf_properties, uri_dictionnary):
        """ Add an uri and rdf properties to an existing uri_dictionnary IN PLACE"""
        uri = self.normalize_uri(uri)
        actual_dict = uri_dictionnary.get(uri, {})
        for rdf_prop, values in rdf_properties.iteritems():
            actual_dict.setdefault(rdf_prop, []).extend(values)
        uri_dictionnary[uri] = actual_dict

    def is_external_uri(self, uri):
        """ Check if this uri should be considered as an external uri. """
        if self.base_uri and not uri.startswith(self.base_uri):
            return True
        elif self.externaluri_callback:
            if self.externaluri_callback(uri):
                return True
        return False

    ###########################################################################
    ### REGISTRATION FUNCTIONS ################################################
    ###########################################################################
    def register_base_uri(self, uri):
        """ Register the base uri for ExternalUri creation triggering in relations
        (i.e. create an exteral uris for all the relations that don't respect this base_uri).
        """
        self.base_uri = uri

    def register_prefix(self, prefix, xmlns, overwrite=False):
        """ Register a prefix/namespace """
        self.namespaces[prefix] = xmlns
        self.reverse_namespaces[xmlns] = prefix
        self.prefixes[prefix] = xmlns

    def register_uri_conversion_callback(self, callback):
        """ Registering the uri conversion callback """
        self.uri_conversion_callback = callback

    def register_etype_callback(self, callback):
        """ Registering a callback for etype guessing """
        self.etype_callback = callback

    def register_attribute_callback(self, yamssnippet, func):
        self.attributes_callbacks[self._norm_yams_key(yamssnippet)] = func

    def register_relation_callback(self, yamssnippet, func):
        self.relations_callbacks[self._norm_yams_key(yamssnippet)] = func

    def register_relations_etype_callbacks(self, rtype, func):
        self.relations_etype_callbacks[rtype] = func

    def register_externaluri_callback(self, callback):
        """ Registering the external uri checking callback """
        self.externaluri_callback = callback

    def register_rdf_etype_property(self, rdf_etype_property):
        """ Register a new rdf_etype_property"""
        self.rdf_etype_property = rdf_etype_property

    def register_concatenation_str(self, concatenation_str):
        """ Register a new concatenation string"""
        self.concatenation_str = concatenation_str

    def register_allow_multiple_values(self, allow_multiple_values):
        """ Register a new allow_multiple_values to allow (or not)
        multiple values for an attribute"""
        self.allow_multiple_values = allow_multiple_values

    def get_attribute_callback(self, etype, attr):
        """ Return a attribute callback for a given etype and attr
        """
        func = self.attributes_callbacks.get((etype, attr, '*'))
        if func:
            return func
        return self.attributes_callbacks.get(('*', attr, '*'))

    def get_relation_callback(self, etype, rtype, etype_to=None):
        """ Return a relation callback for a given etype and rtype
        """
        if etype_to:
            func = self.relations_callbacks.get((etype, rtype, etype_to))
            if func:
                return func
        func = self.relations_callbacks.get((etype, rtype, '*'))
        if func:
            return func
        return self.relations_callbacks.get(('*', rtype, '*'))

    ###########################################################################
    ### SCHEMA HANDLING #######################################################
    ###########################################################################
    def register_schema(self, schema):
        """ Register the schema for mapping """
        self.schema = schema
        # Get attributes
        for eschema in schema.entities():
            etype = eschema.type
            etype_dict = self.attributes_by_etype.setdefault(etype, {})
            eschema = self.schema.eschema(etype)
            for attr in eschema.attribute_definitions():
                etype_dict[attr[0].type] = attr[1].type
            # Add inlined relations
            inlined_dict = self.inlined_relations_by_etype.setdefault(etype, {})
            for rschema in eschema.relation_definitions():
                if rschema[0].inlined:
                    etypes = (r.type for r in rschema[1])
                    inlined_dict[rschema[0].type] = etypes

    ###########################################################################
    ### ETYPE HANDLING ########################################################
    ###########################################################################
    def guess_etype(self, rdf_properties):
        """ Guess an etype from a dictionnary of rdf properties """
        # 1 - Try a specific callback
        # We do it FIRST because it can override the basic logic
        # based on rdf type
        types = [normalize_xml(p, self.reverse_namespaces)
                 for p, t in rdf_properties.get(self.rdf_etype_property, [])]
        types = sorted(types, key= lambda x: x=='skos:Concept')
        if self.etype_callback is not None:
            etype = self.etype_callback(rdf_properties, types)
            if etype:
                return etype
        # 2 - Get all the properties related to the rdf property
        # used for etype guessing. Try skos:Concept at last (too general)
        for _type in types:
            try:
                etype = self.yeq(_type, isentity=True)[0]
                return etype
            except:
                continue

    def iterate_attributes_from_rdf(self, rdf_properties, etype, attr, attrtype):
        """ Try to convert a rdf value to attributes using the XY mapping
        """
        rdfsnippets = self.xeq('%s %s' % (etype, attr))
        if not rdfsnippets:
            # No rdfsnippet, continue
            return
        # There are some rdf snippets - Use them to retrieve the
        # rdf to attributes name mapping
        for _, (uri_ns, uri_part), __ in rdfsnippets:
            # XXX Better way to get the snippet ?
            rdfsnippet =  ':'.join([self.reverse_namespaces.get(uri_ns, uri_ns), uri_part])
            # Existing rdfsnippet, get attribute and convert it
            attrvalues = rdf_properties.get(rdfsnippet)
            if not attrvalues:
                continue
            for value, rdf_type in attrvalues:
                values = self.attributes_callbacks.get(attrtype)(value)
                if not isinstance(values, (list, tuple)):
                    yield values
                else:
                    for value in values:
                        yield value

    def _build_attr_values_for_etype(self, rdf_properties, etype, attr, attrtype):
        """ Build a list of values for attributes (or inlined relations) for a given etype
        """
        # Check first if it exists a specific callback
        # for computing the attributes
        func = self.get_attribute_callback(etype, attr)
        if func:
            values = func(rdf_properties)
            if not isinstance(values, (tuple, list)):
                return (values,)
            return values
        values = []
        # Then, try to see if there exists an RDF->YAMS correspondance
        for value in self.iterate_attributes_from_rdf(rdf_properties, etype, attr, attrtype):
            values.append(value)
        return values

    def build_entity_from_rdf(self, rdf_properties, etype):
        """ Build a dictionnary for the entity from the rdf properties
        and the given etype. """
        entity = {}
        for attr, attrtype in self.attributes_by_etype[etype].iteritems():
            # Do not deal with meta attributes
            if attr in META_ATTRIBUTES:
                continue
            # Add values to entity
            values = self._build_attr_values_for_etype(rdf_properties, etype, attr, attrtype)
            if values:
                entity.setdefault(attr, []).extend(values)
        # Merge attributes and return new entity
        return self.merge_entity(entity)

    def build_inlined_relations(self, rdf_properties, etype):
        """ Build a dictionnary for the inlined relations from the rdf properties
        and the given etype. """
        # Add inlined relations
        relations = {}
        for rtype, _type in self.inlined_relations_by_etype[etype].iteritems():
            values = self._build_attr_values_for_etype(rdf_properties, etype, rtype, _type)
            if values:
                # ONLY ONE VALUE (inlined relation) -> Force it
                relations[attr] = [values[0]]
        return relations

    def merge_entity(self, entity):
        """ Merge the attributes of an entity, with possible concatenation.
        """
        new_entity = {}
        for attr, values in entity.iteritems():
            if len(values) == 1:
                value = values[0]
            elif len(values)>1 and isinstance(values[0], basestring):
                if self.concatenation_str:
                    # We have multiple strings, we join them
                    value = self.concatenation_str.join(values)
                else:
                    # No concatenation string given, keep first values
                    value = values[0]
            else:
                # We have multiple attributes, that are not string.
                if not self.allow_multiple_values:
                    # We do nothing
                    print 'Multiple values for', attr, values
                    print 'Do not keep anything (see allow_multiple_values attribute of XY)'
                    continue
                else:
                    values = [v for v in values if v is not None]
                    if values:
                        value = values[0]
                    else:
                        continue
            new_entity[attr] = value
        return new_entity


    ###########################################################################
    ### RELATIONS HANDLING ####################################################
    ###########################################################################
    def relations_from_rdf(self, rdf_properties, etype):
        """ Iterate the relations from rdf properties, if there exists a mapping
        """
        relations = {}
        for predicate, object_values in rdf_properties.iteritems():
            try:
                mapping = self.yeq(predicate)
            except UnsupportedVocabulary:
                continue
            if not mapping:
                continue
            if not etype and predicate == 'rdf:about':
                # Deals with issue with no etype
                continue
            computed_mapping = set()
            for (s, r, o) in mapping:
                if (s in ('*', etype) or etype is None):
                    if o == '*' and self.schema:
                        # Iterate over all the possible etypes
                        for o in self.schema.rschema(r).objects():
                            computed_mapping.add((s, r, o.type))
                    else:
                        computed_mapping.add((s, r, o))
            for (_subject, _relation, _object) in computed_mapping:
                # Do not dealt with attributes
                if etype and _relation in self.attributes_by_etype[etype]:
                    continue
                # Keep both parts of the relation as we do not know the etype
                _etypes = (etype or _subject, _object)
                _object_values = [self.attributes_callbacks['String'](obj)
                                  for obj, typ in object_values]
                rels = _object_values
                # Convert if necessary
                rtype_callback = self.get_relation_callback(_etypes[0], _relation,
                                                            _etypes[1])
                if rtype_callback:
                    rels = [rtype_callback(r, predicate, rdf_properties) for r in rels]
                relations.setdefault(_relation, {}).setdefault(_etypes, set()).update(rels)
        return relations


    ###########################################################################
    ### RDF GENERATION ########################################################
    ###########################################################################
    def etype_to_rdf(self, etype):
        """ Iterate rdf object for etype """
        for item in self.xeq(etype):
            # For an etype, we only have a tuple of one couple
            yield ''.join(item[0])

    def relation_to_rdf(self, etype, attr, role='subject'):
        """ Iterate rdf relation for rtype """
        if role == 'subject':
            yamssnippet = '%s %s *' % (etype, attr)
        else:
            yamssnippet = '* %s %s' % (attr, etype)
        for item in self.xeq(yamssnippet):
            # For an attribute, we have ('*', couple, '*')
            yield ''.join(item[1])

    def iter_entity_triples(self, entity):
        """ Iter the attributes triples """
        etype = entity.e_schema.type
        cwuri = entity.cwuri
        for rschema, eschemas, role in entity.e_schema.relation_definitions('relation'):
           rtype = rschema.type
           # Skip some relations
           if rtype in SKIP_RTYPES or rtype.endswith('_permission'):
               continue
           for eschema in eschemas:
               if eschema.final:
                   # Attribute
                   try:
                       value = entity.cw_attr_cache[rtype]
                   except KeyError:
                       continue # assuming rtype is Bytes
                   if value is not None:
                       for rel in self.relation_to_rdf(etype, rtype):
                           yield (cwuri, rel, value, 'literal')
               else:
                   # Relation
                       for rel in self.relation_to_rdf(etype, rtype, role=role):
                           for related in entity.related(rtype, role, entities=True, safe=True):
                               if role == 'subject':
                                   yield (cwuri, rel, related.cwuri, 'resource')
                               else:
                                   yield (related.cwuri, rel, cwuri, 'resource')


###############################################################################
### CONCRETE INSTANTIATION ####################################################
###############################################################################
XY = DataioXY()
register_prefix = XY.register_prefix
register_uri_conversion_callback = XY.register_uri_conversion_callback
add_equivalence = XY.add_equivalence
register_etype_callback = XY.register_etype_callback
register_attribute_callback = XY.register_attribute_callback
register_relation_callback = XY.register_relation_callback
register_base_uri = XY.register_base_uri
register_externaluri_callback = XY.register_externaluri_callback
register_rdf_etype_property = XY.register_rdf_etype_property
register_concatenation_str = XY.register_concatenation_str
register_allow_multiple_values = XY.register_allow_multiple_values
register_relations_etype_callbacks = XY.register_relations_etype_callbacks
