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

from cubes.dataio.interfaces import (CSVRdfReader, CSVRdfWriter, DictFobj,
                                     build_rdf_reader, build_rdf_writer,
                                     convert_string, convert_int,
                                     convert_float, convert_date,
                                     normalize_xml, split_uri, build_uri_dict)

HERE = osp.abspath(osp.dirname(__file__))

RDF_DATA = set([(u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://dbpedia.org/ontology/abstract',
                 u'Taman Scientex is a township in Pasir Gudang, '
                 u'Johor, Malaysia. This townships is located '
                 u'between Masai and Pasir Gudang.',
                 'literal'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://xmlns.com/foaf/0.1/isPrimaryTopicOf',
                 u'http://en.wikipedia.org/wiki/Taman_Scientex',
                 'resource'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://www.w3.org/2000/01/rdf-schema#label',
                 u'Taman Scientex',
                 'literal'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://www.w3.org/ns/prov#wasDerivedFrom',
                 u'http://en.wikipedia.org/wiki/Taman_Scientex?oldid=412881153',
                 'resource'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://www.w3.org/2002/07/owl#sameAs',
                 u'http://rdf.freebase.com/ns/m.06wb2yz',
                 'resource'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://dbpedia.org/property/hasPhotoCollection',
                 u'http://www4.wiwiss.fu-berlin.de/flickrwrappr/photos/Taman_Scientex',
                 'resource'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://www.w3.org/2000/01/rdf-schema#comment',
                 u'Taman Scientex is a township in Pasir Gudang, '
                 u'Johor, Malaysia. This townships is located '
                 u'between Masai and Pasir Gudang.',
                 'literal'),
                (u'http://dbpedia.org/resource/Taman_Scientex',
                 u'http://purl.org/dc/terms/subject',
                 u'http://dbpedia.org/resource/Category:Towns_and_'
                 u'suburbs_in_Johor_Bahru_District',
                 'resource')
                ])


CSV_DATA_1 = set([('line 0', 'row 0', u'1024032', 'literal'),
                  ('line 1', 'row 0', u'1024034', 'literal'),
                  ('line 7', 'row 16', u'211', 'literal'),
                  ('line 7', 'row 17', u'Europe/Paris', 'literal'),
                  ('line 10', 'row 7', u'PPL', 'literal'), ('line 9', 'row 8', u'FR', 'literal'),
                ])

CSV_DATA_2 = set([('line 0', 'geoid', u'1024032', 'literal'),
                  ('line 1', 'geoid', u'1024034', 'literal'),
                  ('line 2', 'name', u'Rocher Sud', 'literal'),
                  ('line 2', 'longitude', u'47.3', 'literal'),
                  ])

CSV_DATA_3 = set([('1024034', 'name', u'Île du Lys', 'literal'),
                  ('1024035', 'name', u'Rocher Sud', 'literal'),
                  ('1024036', 'longitude', u'47.33333', 'literal'),
                  ])


class CsvReaderTC(testlib.CubicWebTC):
    def setUp(self):
        self.filename = osp.join(HERE, 'data/FR.txt')

    def test_csv_no_fields(self):
        reader = CSVRdfReader()
        triples = reader.iterate_triples_from_file(self.filename,
                                                   separator='\t',
                                                   uri_ind=None)
        results = [i for i in triples]
        for triple in CSV_DATA_1:
            self.assertIn(triple, results)

    def test_csv_fields(self):
        reader = CSVRdfReader({0: u'geoid', 1:u'name', 5: 'longitude'})
        triples = reader.iterate_triples_from_file(self.filename,
                                                   separator='\t',
                                                   limit = 3,
                                                   uri_ind=None)
        results = [i for i in triples]
        for triple in CSV_DATA_2:
            self.assertIn(triple, results)

    def test_csv_fields_id(self):
        reader = CSVRdfReader({1:u'name', 5: 'longitude'})
        triples = reader.iterate_triples_from_file(self.filename,
                                                   separator='\t',
                                                   limit = 3,
                                                   uri_ind=0)
        results = [i for i in triples]
        for triple in CSV_DATA_3:
            self.assertIn(triple, results)


class CsvWriterTC(testlib.CubicWebTC):

    def setUp(self):
        self.data = CSV_DATA_3

    def test_csv_fields_id(self):
        # Write data
        tmp_filename = 'tmp_rdf_test.txt'
        writer = CSVRdfWriter(separator='\t')
        for _s, _p, _o, _ot in self.data:
            writer.add_triple(_s, _p, _o, _ot)
        writer.write_file(tmp_filename)
        # Read them for test
        reader = CSVRdfReader({1:u'name', 2: 'longitude'})
        triples = reader.iterate_triples_from_file(tmp_filename,
                                                   separator=',',
                                                   limit = 2,
                                                   uri_ind=0)
        results = set([i for i in triples])
        self.assertEqual(self.data, results)


class RdfReaderTC(testlib.CubicWebTC):
    def setUp(self):
        self.wanted = RDF_DATA

    def _test_format(self, library, formats):
        for _format in formats:
            reader = build_rdf_reader(library=library, rdf_format=_format,
                               _encoding='unicode_escape')
            filename = osp.join(HERE, 'data/Taman_Scientex.%s' % _format)
            triples = reader.iterate_triples_from_file(filename)
            results = set([i for i in triples])
            self.assertEqual(self.wanted, results)

    def test_raw(self):
        self._test_format('rawnt', ['nt'])

    def test_rdflib(self):
        self._test_format('rdflib', ['nt', 'rdf'])

    def test_librdf(self):
        self._test_format('librdf', ['nt', 'rdf'])


class RdfWriterTC(testlib.CubicWebTC):

    def setUp(self):
        self.data = RDF_DATA

    def _test_format(self, library, format, with_ot=True):
        # Write data
        tmp_filename = 'tmp_rdf_test.txt'
        writer = build_rdf_writer(library=library, _encoding='utf-8')
        for _s, _p, _o, _ot in self.data:
            if not with_ot:
                _ot = None
            writer.add_triple(_s, _p, _o, _ot)
        writer.write_file(tmp_filename, rdf_format=format)
        # Read them for test
        reader = build_rdf_reader(library=library,
                                  rdf_format=format,
                                  _encoding='utf-8')
        triples = reader.iterate_triples_from_file(tmp_filename)
        results = set([i for i in triples])
        self.assertEqual(self.data, results)

    def test_raw(self):
        value = self._test_format('rawnt', 'nt')

    def test_raw_without_type(self):
        value = self._test_format('rawnt', 'nt', with_ot=False)

    def test_rdflib(self):
        for _format in ('nt', 'n3', 'rdf'):
            value = self._test_format('rdflib', _format)

    def test_rdflib_without_type(self):
        for _format in ('nt', 'n3', 'rdf'):
            value = self._test_format('rdflib', _format, with_ot=False)

    def test_librdf(self):
        for _format in ('nt', 'n3', 'rdf'):
            value = self._test_format('librdf', _format)

    def test_librdf_without_type(self):
        for _format in ('nt', 'n3', 'rdf'):
            value = self._test_format('librdf', _format, with_ot=False)


class ConverterTC(testlib.CubicWebTC):

    def test_convert_string(self):
        self.assertEqual(convert_string('toto'), 'toto')

    def test_convert_int(self):
        self.assertEqual(convert_int('11'), 11)
        self.assertEqual(convert_int('X11'), None)

    def test_convert_float(self):
        self.assertEqual(convert_float('12.'), 12.)
        self.assertEqual(convert_float('X12'), None)
        self.assertEqual(convert_float('12,3'), 12.3)

    def test_convert_date(self):
        date = convert_date('14-11-2012')
        self.assertEqual(date.day, 14)
        self.assertEqual(date.month, 11)
        self.assertEqual(date.year, 2012)
        date = convert_date('2012-11-14', datetime_format='%Y-%m-%d')
        self.assertEqual(date.day, 14)
        self.assertEqual(date.month, 11)
        self.assertEqual(date.year, 2012)


class RDFUtilitiesTC(testlib.CubicWebTC):

    def test_split_uri(self):
        self.assertEqual(split_uri("http://rdvocab.info/uri/schema/FRBRentitiesRDA/Manifestation"),
                          ("http://rdvocab.info/uri/schema/FRBRentitiesRDA/" , "Manifestation"))
        self.assertEqual(split_uri("http://www.w3.org/2004/02/skos/core#concept"),
                          ("http://www.w3.org/2004/02/skos/core#", "concept"))

    def test_normalize_xml(self):
        self.assertEqual(normalize_xml("http://rdvocab.info/uri/schema/FRBRentitiesRDA/Manifestation"),
                         'frbr:Manifestation')
        self.assertEqual(normalize_xml("http://www.w3.org/2004/02/skos/core#concept"),
                         'skos:concept')
        self.assertEqual(normalize_xml("http://www.w3.org/test#concept"),
                         "http://www.w3.org/test#:concept")


    def test_build_uri_dict(self):
        filename = osp.join(HERE, 'data/Taman_Scientex.rdf')
        uri_dict = build_uri_dict((filename,), library='rdflib')
        self.assertTrue('http://dbpedia.org/resource/Taman_Scientex' in uri_dict)
        rdf_properties = uri_dict['http://dbpedia.org/resource/Taman_Scientex']
        self.assertEqual(rdf_properties['http://purl.org/dc/terms/subject'],
                         [(u'http://dbpedia.org/resource/Category:Towns_and_suburbs_in_Johor_Bahru_District',
                           'resource')])
        self.assertEqual(rdf_properties[u'http://www.w3.org/ns/prov#wasDerivedFrom'],
                         [(u'http://en.wikipedia.org/wiki/Taman_Scientex?oldid=412881153', 'resource')])

    def test_mmap(self):
        filename = osp.join(HERE, 'data/mmap.csv')
        mmap = DictFobj(filename, separator=',', cast_type=int)
        mmap.fit()
        self.assertEqual(len(mmap.internal_dict), 3)
        self.assertEqual(mmap.get(1)[1], 'Toto')
        self.assertEqual(mmap.get(2)[1], 'Tata')
        self.assertEqual(mmap.get(1)[1], 'Toto')

    def test_mmap2(self):
        filename = osp.join(HERE, 'data/mmap2.csv')
        mmap = DictFobj(filename, separator=',', cast_type=int)
        mmap.fit(index_key=1)
        self.assertEqual(len(mmap.internal_dict), 3)
        self.assertEqual(mmap.get(1)[2], 'Toto')
        self.assertEqual(mmap.get(2)[2], 'Tata')
        self.assertEqual(mmap.get(1)[2], 'Toto')

    def test_mmap3(self):
        filename = osp.join(HERE, 'data/mmap.csv')
        mmap = DictFobj(filename, separator=',')
        mmap.fit()
        self.assertEqual(len(mmap.internal_dict), 3)
        self.assertEqual(mmap.get('1')[1], 'Toto')
        self.assertEqual(mmap.get('2')[1], 'Tata')
        self.assertEqual(mmap.get('1')[1], 'Toto')


if __name__ == '__main__':
    from logilab.common.testlib import unittest_main
    unittest_main()
