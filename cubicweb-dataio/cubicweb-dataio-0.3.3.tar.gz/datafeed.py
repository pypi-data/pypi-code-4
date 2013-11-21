# -*- coding: utf-8 -*-
import urllib
import json

from cubicweb.server.sources import datafeed
from cubicweb.dataimport import SQLGenObjectStore

from cubes.dataio.xy import XY
from cubes.dataio.dataimport import RDFStore
from cubes.dataio.interfaces import URI_RDF_PROP


class SparqlParser(datafeed.DataFeedParser):
    """datafeed parser for sparql-based feeds

    The url should be of the form: endpoint###query

    Example:
        >>> url = u'http://demo.cubicweb.org/sparql###SELECT ?x WHERE {?x a foaf:Person} LIMIT 1000'
        >>> session.create_entity('CWSource', name=u'dbpedia-sparql', type=u'datafeed',
                                  parser=u'sparql-parser', url=url,
                                  config=u'synchronization-interval=120min')
    """
    __regid__ = 'sparql-parser'

    def process(self, url, raise_on_error=False):
        """main callback: process the url"""
        # Get results
        endpoint,query = url.split('###')
        complete_query = u'''SELECT ?x ?y ?r WHERE  { ?x ?r ?y {%s}}''' % query
        _format = u'json'
        sparql_url = '%s?%s' % (endpoint, urllib.urlencode({'query': complete_query,
                                                            'results': _format, 'output': _format}))
        results = urllib.urlopen(sparql_url).read()
        results = json.loads(results)
        # Create triples for import
        uri_dictionnary = {}
        for triple in results['results']['bindings']:
            uri  = triple['x']['value']
            uri_dictionnary.setdefault(uri, {})[URI_RDF_PROP] = [(uri, 'resource'),]
            _predicate = triple['r']['value']
            _object = triple['y']['value']
            _type = triple['y']['type']
            _type = 'resource' if _type == 'uri' else 'literal'
            uri_dictionnary[uri].setdefault(_predicate, []).append((_object, _type))
        # Push data
        external_uris = dict(self._cw.execute('Any U, X WHERE X is ExternalUri, X uri U'))
        existing_uris = set([r[0] for r in self._cw.execute('Any U WHERE X cwuri U')])
        internal_store = SQLGenObjectStore(self._cw)
        store = RDFStore(self._cw, XY,
                         internal_store=internal_store,
                         external_uris_dict=external_uris)
        for uri, rdf_properties in uri_dictionnary.iteritems():
            if uri not in existing_uris:
                entity = store.create_entity(rdf_properties)
                existing_uris.add(uri)
        internal_store.flush()
        internal_store.commit()
        store.flush()
        store.convert_all_relations()
        store.cleanup()
