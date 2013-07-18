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

import os.path as osp
from cStringIO import StringIO
from cubicweb.devtools import testlib

from cubes.dataio import interfaces, dataimport
from cubes.dataio.xy import XY
from cubes.dataio.test import DISEASOME_SCHEMA


HERE = osp.abspath(osp.dirname(__file__))



class FakeEntity(dict):
    """ Fake entity for test """
    @property
    def eid(self):
        return 1

class FakeInternalStore(object):
    """ Fake store for test """
    def create_entity(self, etype, **kwargs):
        entity = FakeEntity(kwargs)
        entity['etype'] = etype
        return entity


class DataImportTC(testlib.CubicWebTC):

    def test_import_rdf_store(self):
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
        # Get filenames
        filename = osp.join(HERE, 'data/diseasome_sample.nt')
        # Create the RDF store
        internal_store = FakeInternalStore()
        uri_dictionnary = interfaces.build_uri_dict((filename,),
                                                    library='rdflib',
                                                    rdf_format='nt')
        uri_dictionnary = XY.merge_uri_dictionnary(uri_dictionnary)
        store = dataimport.RDFStore(self.session, XY, internal_store=internal_store)
        store._initialized['relations_tuple'] = set([('Disease', 'close_match', 'ExternalUri'),
                                                     ('Disease', 'subtype_of', 'Disease'),
                                                     ('Disease', 'associated_genes', 'Gene'),
                                                     ('Disease', 'possible_drugs', 'ExternalUri'),
                                                     ('Disease', 'omim', 'ExternalUri'),
                                                     ('Disease', 'omim_page', 'ExternalUri'),
                                                     ('Disease', 'chromosomal_location', 'ExternalUri'),
                                                     ('Disease', 'sameas', 'ExternalUri'),
                                                     ('Gene', 'sameas', 'ExternalUri'),
                                                     ('ExternalUri', 'sameas', 'ExternalUri'),
                                                     ('Gene', 'gene_id', 'ExternalUri'),
                                                     ('Gene', 'hgnc_id', 'ExternalUri'),
                                                     ('Gene', 'hgnc_page', 'ExternalUri'),
                                                     ('Gene', 'bio2rdf_symbol', 'ExternalUri')])
        # Unregister schema
        XY.schema = None
        # Import entities
        entities = []
        for uri, rdf_properties in uri_dictionnary.iteritems():
            entity = store.create_entity(rdf_properties)
            if entity:
                entities.append(entity)
        self.assertEqual(len(entities), 342)


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
