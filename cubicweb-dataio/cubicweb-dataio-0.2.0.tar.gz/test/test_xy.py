# -*- coding: utf-8 -*-
# copyright 2012 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

from cubicweb.devtools import testlib

from cubes.dataio.interfaces import normalize_xml
from cubes.dataio.xy import DataioXY
from cubes.dataio.test import DISEASOME_SCHEMA


class XYTC(testlib.CubicWebTC):

    def test_xy_add_equivalence_etype(self):
        xy = DataioXY()
        xy.register_prefix('nyt', 'http://data.nytimes.com/elements/')
        xy.add_equivalence('People', 'nyt:nytd_per')
        _type = normalize_xml('http://data.nytimes.com/elements/nytd_per', xy.reverse_namespaces)
        self.assertEqual(xy.yeq(_type, isentity=True)[0], 'People')

    def test_xy_guess_etype(self):
        xy = DataioXY()
        xy.register_prefix('nyt', 'http://data.nytimes.com/elements/')
        xy.add_equivalence('People', 'nyt:nytd_per')
        rdf_properties = {'rdf:type': (('http://data.nytimes.com/elements/nytd_per', 'resource'),)}
        self.assertEqual(xy.guess_etype(rdf_properties), 'People')

    def test_xy_guess_etype_callback(self):
        xy = DataioXY()
        xy.register_prefix('nyt', 'http://data.nytimes.com/elements/')
        xy.add_equivalence('People', 'nyt:nytd_per')
        rdf_properties = {'rdf:label': (('I am a people', 'literal'),)}
        def etype_callback(rdf_props):
            if 'rdf:label' in rdf_props:
                if 'people' in rdf_props['rdf:label'][0][0]:
                    return 'People'
        xy.register_etype_callback(etype_callback)
        self.assertEqual(xy.guess_etype(rdf_properties), 'People')
        rdf_properties = {'rdf:label': (('I am a location', 'literal'),)}
        self.assertEqual(xy.guess_etype(rdf_properties), None)

    def test_xy_add_equivalence(self):
        xy = DataioXY()
        xy.add_equivalence('* pref_label', 'skos:prefLabel')
        xy.register_schema(self.schema)
        uri = normalize_xml('http://www.w3.org/2004/02/skos/core#prefLabel', xy.reverse_namespaces)
        self.assertEqual(xy.yeq(uri), [('*', 'pref_label', '*')])

    def test_xy_add_equivalence_2(self):
        xy = DataioXY()
        xy.add_equivalence('CWUser pref_label', 'skos:prefLabel')
        xy.register_schema(self.schema)
        uri = normalize_xml('http://www.w3.org/2004/02/skos/core#prefLabel', xy.reverse_namespaces)
        self.assertEqual(xy.yeq(uri), [('CWUser', 'pref_label', '*')])

    def test_xy_normalize_uri(self):
        xy = DataioXY()
        def uri_callback(uri):
            return uri.split('/')[-1]
        xy.register_uri_conversion_callback(uri_callback)
        self.assertEqual(xy.normalize_uri('http://data.nytimes.com/64870337666324078863'),
                         '64870337666324078863')

    def test_xy_merge_uri_dictionnary(self):
        xy = DataioXY()
        dict1 = {'http://plap/toto': {'rdf:type': (('http://data.nytimes.com/elements/nytd_per', 'resource'),)},
                 'http://plap/tata': {'rdf:type': (('http://data.nytimes.com/elements/nytd_per', 'resource'),)},
                 'http://plop/toto': {'skos:prefLabel': (('toto', 'literal'),)},}
        def uri_callback(uri):
            return uri.split('/')[-1]
        xy.register_uri_conversion_callback(uri_callback)
        merged_dict = xy.merge_uri_dictionnary(dict1)
        self.assertEqual(len(merged_dict), 2)
        self.assertTrue('toto' in merged_dict)
        self.assertTrue('tata' in merged_dict)
        self.assertEqual(len(merged_dict['toto']), 2)
        self.assertTrue('rdf:type' in merged_dict['toto'])
        self.assertTrue('skos:prefLabel' in merged_dict['toto'])

    def test_xy_add_to_existing_uri_dictionnary(self):
        xy = DataioXY()
        dict1 = {'http://plap/toto': {'rdf:type': (('http://data.nytimes.com/elements/nytd_per', 'resource'),)},
                 'http://plap/tata': {'rdf:type': (('http://data.nytimes.com/elements/nytd_per', 'resource'),)}}
        xy.add_to_existing_uri_dictionnary('http://plap/toto', {'skos:prefLabel': (('toto', 'literal'),)},
                                           dict1)
        self.assertTrue('rdf:type' in dict1['http://plap/toto'])
        self.assertTrue('skos:prefLabel' in dict1['http://plap/toto'])

    def test_xy_is_external_uri(self):
        xy = DataioXY()
        xy.register_base_uri('http://data.nytimes.com/')
        self.assertTrue(xy.is_external_uri('http://plap/toto'))
        self.assertFalse(xy.is_external_uri('http://data.nytimes.com/toto'))

    def test_xy_is_external_uri_callback(self):
        xy = DataioXY()
        xy.register_base_uri('http://data.nytimes.com/')
        def externaluri_callback(uri):
            return True if 'plap' in uri else False
        xy.register_externaluri_callback(externaluri_callback)
        self.assertTrue(xy.is_external_uri('http://plap/toto'))
        self.assertFalse(xy.is_external_uri('http://data.nytimes.com/toto'))
        self.assertTrue(xy.is_external_uri('http://data.nytimes.com/plap/toto'))

    def test_xy_register_schema(self):
        xy = DataioXY()
        self.assertFalse('CWUser' in xy.attributes_by_etype)
        xy.register_schema(self.schema)
        self.assertTrue('CWUser' in xy.attributes_by_etype)
        self.assertTrue('login' in xy.attributes_by_etype['CWUser'])

    def test_xy_iterate_attributes_from_rdf(self):
        xy = DataioXY()
        xy.register_schema(self.schema)
        xy.add_equivalence('* login', 'skos:prefLabel')
        rdf_properties = {'skos:prefLabel': (('toto', 'literal'),)}
        attributes = list(xy.iterate_attributes_from_rdf(rdf_properties, 'CWUser', 'login', 'String'))
        self.assertEqual(attributes, ['toto',])

    def test_xy_build_attr_values_for_etype(self):
        xy = DataioXY()
        xy.register_schema(self.schema)
        xy.add_equivalence('* login', 'skos:prefLabel')
        rdf_properties = {'skos:prefLabel': (('toto', 'literal'),)}
        attributes = xy._build_attr_values_for_etype(rdf_properties, 'CWUser', 'login', 'String')
        self.assertEqual(attributes, ['toto',])

    def test_xy_build_attr_values_for_etype_callback(self):
        xy = DataioXY()
        xy.register_schema(self.schema)
        xy.add_equivalence('* login', 'skos:prefLabel')
        rdf_properties = {'skos:prefLabel': (('toto', 'literal'),)}
        def attribute_callback(rdf_props):
            return rdf_props['skos:prefLabel'][0][0][:2]
        xy.register_attribute_callback('* login', attribute_callback)
        attributes = xy._build_attr_values_for_etype(rdf_properties, 'CWUser', 'login', 'String')
        self.assertEqual(attributes, ('to',))

    def test_xy_build_entity_from_rdf(self):
        xy = DataioXY()
        xy.register_schema(self.schema)
        xy.add_equivalence('CWUser login', 'skos:prefLabel')
        xy.add_equivalence('* cwuri', 'rdf:about')
        rdf_properties = {'skos:prefLabel': (('toto', 'literal'),),
                          'rdf:about': (('http://plop/toto', 'literal'),)}
        entity = xy.build_entity_from_rdf(rdf_properties, 'CWUser')
        self.assertEqual(entity, {'cwuri': 'http://plop/toto', 'login': 'toto'})
        entity = xy.build_entity_from_rdf(rdf_properties, 'ExternalUri')
        self.assertEqual(entity, {'cwuri': 'http://plop/toto'})

    def test_xy_merge_entity(self):
        xy = DataioXY()
        xy.register_schema(self.schema)
        xy.register_concatenation_str(' - ')
        xy.add_equivalence('CWUser login', 'skos:prefLabel')
        xy.add_equivalence('* cwuri', 'rdf:about')
        rdf_properties = {'skos:prefLabel': (('toto', 'literal'), ('tata', 'literal')),
                          'rdf:about': (('http://plop/toto', 'literal'),)}
        entity = xy.build_entity_from_rdf(rdf_properties, 'CWUser')
        self.assertEqual(entity, {'cwuri': 'http://plop/toto', 'login': 'toto - tata'})
        xy.register_concatenation_str(' . - ')
        entity = xy.build_entity_from_rdf(rdf_properties, 'CWUser')
        self.assertEqual(entity, {'cwuri': 'http://plop/toto', 'login': 'toto . - tata'})
        xy.register_concatenation_str(None)
        entity = xy.build_entity_from_rdf(rdf_properties, 'CWUser')
        self.assertEqual(entity, {'cwuri': 'http://plop/toto', 'login': 'toto'})

    def test_xy_relations_from_rdf(self):
        xy = DataioXY()
        xy.register_schema(self.schema)
        xy.add_equivalence('CWUser same_as ExternalUri', 'owl:sameAs')
        rdf_properties = {'owl:sameAs': (('http://plop/tata', 'literal'),)}
        relations = xy.relations_from_rdf(rdf_properties, 'CWUser')
        self.assertEqual(relations, {'same_as': {('CWUser', 'ExternalUri'): set(['http://plop/tata'])}})


class XYGenerationTC(testlib.CubicWebTC):

    @classmethod
    def setUpClass(cls):
        from cubes.dataio.xy import XY
        # Add False schema
        XY.attributes_by_etype = DISEASOME_SCHEMA
        # Add XY
        XY.register_base_uri('http://www4.wiwiss.fu-berlin.de/diseasome/resource/')
        XY.register_prefix('diseasome', 'http://www4.wiwiss.fu-berlin.de/diseasome/resource/diseasome/')
        def externaluri_callback(uri):
            if uri.startswith('http://www4.wiwiss.fu-berlin.de/diseasome/resource/'):
                if uri.endswith('disease') or uri.endswith('gene'):
                    return False
                return True
            return True
        XY.register_externaluri_callback(externaluri_callback)
        XY.add_equivalence('Gene', 'diseasome:genes')
        XY.add_equivalence('Disease', 'diseasome:diseases')
        XY.add_equivalence('* name', 'diseasome:name')
        XY.add_equivalence('* label', 'rdfs:label')
        XY.add_equivalence('* label', 'diseasome:label')
        XY.add_equivalence('* class_degree', 'diseasome:classDegree')
        XY.add_equivalence('* size', 'diseasome:size')
        XY.add_equivalence('Disease close_match ExternalUri', 'diseasome:classes')
        XY.add_equivalence('Disease subtype_of Disease', 'diseasome:diseaseSubtypeOf')
        XY.add_equivalence('Disease associated_genes Gene', 'diseasome:associatedGene')
        XY.add_equivalence('Disease possible_drugs ExternalUri', 'diseasome:possible_drugs')
        XY.add_equivalence('Disease omim ExternalUri', 'diseasome:omim')
        XY.add_equivalence('Disease omim_page ExternalUri', 'diseasome:omimPage')
        XY.add_equivalence('Disease chromosomal_location ExternalUri', 'diseasome:chromosomalLocation')
        XY.add_equivalence('* sameas ExternalUri', 'owl:sameAs')
        XY.add_equivalence('Gene gene_id ExternalUri', 'diseasome:geneId')
        XY.add_equivalence('Gene hgnc_id ExternalUri', 'diseasome:hgncId')
        XY.add_equivalence('Gene hgnc_page ExternalUri', 'diseasome:hgncIdPage')
        XY.add_equivalence('Gene bio2rdf_symbol ExternalUri', 'diseasome:bio2rdfSymbol')
        cls.XY = XY

    def test_rdf_generation_etype(self):
        rdf = [obj for obj in self.XY.etype_to_rdf('Gene')]
        self.assertEqual(rdf, ['http://www4.wiwiss.fu-berlin.de/diseasome/resource/diseasome/genes',])

    def test_rdf_generation_attr(self):
        rdf = [rel for rel in self.XY.relation_to_rdf('Gene', 'label')]
        self.assertEqual(rdf, ['http://www.w3.org/2000/01/rdf-schema#label',
                               'http://www4.wiwiss.fu-berlin.de/diseasome/resource/diseasome/label'])

    def test_rdf_generation_relation(self):
        rdf = [rel for rel in self.XY.relation_to_rdf('Disease', 'associated_genes')]
        self.assertEqual(rdf, ['http://www4.wiwiss.fu-berlin.de/diseasome/resource/diseasome/associatedGene',])

    def test_rdf_generation_relation_object(self):
        rdf = [rel for rel in self.XY.relation_to_rdf('Gene', 'associated_genes', role='object')]
        self.assertEqual(rdf, ['http://www4.wiwiss.fu-berlin.de/diseasome/resource/diseasome/associatedGene',])


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
