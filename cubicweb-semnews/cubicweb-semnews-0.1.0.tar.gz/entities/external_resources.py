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
import rdflib

from cubicweb.selectors import is_instance
from cubicweb.web.views.tabs import LazyViewMixin
from cubicweb.view import EntityView

from cubes.libraryui.views.images import build_carousel

_ = unicode

_SPARQL_CACHE = {}


###############################################################################
### SPARQL TOOLS ##############################################################
###############################################################################
def execute_sparql(query, endpoint):
    """ Execute a query on an endpoint """
    if (query, endpoint) in _SPARQL_CACHE:
        return _SPARQL_CACHE[(query, endpoint)]
    from SPARQLWrapper import SPARQLWrapper, JSON
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        rawresults = sparql.query().convert()
        labels = rawresults['head']['vars']
        results = rawresults["results"]["bindings"]
    except:
        # XXX ?
        print 'OOOOOUPS', query
        results = []
    _SPARQL_CACHE[(query, endpoint)] = results
    return results

def sparql_query_builder(join_variable, triples=None, prefixes=None):
    """ Build a query from a join variable and triples """
    triples = triples or []
    prefixes = prefixes or []
    query_lines = []
    # Prefixes
    for prefix in prefixes:
        query_lines.append('PREFIX %s:<%s>' % prefix)
    # Select
    variables = []
    if join_variable.startswith('http://'):
        join_variable = '<%s>' % join_variable
    else:
        join_variable = '?%s'  % join_variable
        variables.append('%s' % join_variable)
    variables.extend(['?%s' % r['var'] for r in triples
                      if (not 'noselect' in r or not r['noselect'])])
    query_lines.append('SELECT %s' % ' '.join(variables))
    # Where
    query_lines.append('WHERE{')
    for triple in triples:
        rel = triple['rel'] if not triple['rel'].startswith('http://') else ('<%s>' % triple['rel'])
        if triple['var'].startswith('http://'):
            var = '<%s>' % triple['var']
        elif (not 'noselect' in triple or not triple['noselect']):
            var = '?%s' % triple['var']
        else:
            var = triple['var']
        if 'object' not in triple:
            obj = join_variable
        else:
            obj = '?%s' % triple['object']
        if triple.get('role') and triple['role'] == 'subject':
            line = '%s %s %s .' % (var, rel, obj)
        else:
            line = '%s %s %s .' % (obj, rel, var)
        if triple.get('filter'):
            line += '\nFILTER %s' % triple.get('filter')
        if triple.get('optional'):
            line = 'OPTIONAL{%s}' % line
        query_lines.append(line)
    query_lines.append('}')
    return '\n'.join(query_lines)

def lang_order(value, lang_orders=('fr', 'en')):
    if value in lang_orders:
        return lang_orders.index(value)
    return len(lang_orders)+1

def execute_and_merge(uri, endpoint, triples, lang_orders=('fr', 'en')):
    data = {}
    for triple in triples:
        query = sparql_query_builder(uri, triples=(triple,))
        results = execute_sparql(query, endpoint)
        results = [res[triple['var']] for res in results]
        results = [r['value'] for r in sorted(results, key=lambda x:lang_order(x.get('xml:lang')))]
        data[triple['var']] = results[0] if results else None
    return data

def query_match(word, endpoint, query):
    results = execute_sparql(query % {'w': word}, endpoint)
    return [res['uri']['value'] for res in results]


###############################################################################
### DBPEDIA UTILITIES #########################################################
###############################################################################
DBPEDIA_TRIPLES = {'topic':{'var': "topic", 'rel': 'foaf:primaryTopic', 'role': 'subject'},
                   'abstract': {'var': 'abstract', 'rel': 'http://dbpedia.org/ontology/abstract'},
                   'depiction': {'var': 'depiction', 'rel': 'foaf:depiction'},
                   'label': {'var': 'label', 'rel': 'rdfs:label'},
                   'thumbnail': {'var': 'thumbnail', 'rel': 'http://dbpedia.org/ontology/thumbnail'},
                   'latitude': {'var': "latitude", 'rel': 'http://www.w3.org/2003/01/geo/wgs84_pos#lat'},
                   'longitude': {'var': "longitude", 'rel': 'http://www.w3.org/2003/01/geo/wgs84_pos#long'},
                   'geometry': {'var': "geometry", 'rel': 'http://www.w3.org/2003/01/geo/wgs84_pos#geometry'},
                   'subject': {'var': 'subject', 'rel': 'http://purl.org/dc/terms/subject'},
                   'type': {'var': 'type', 'rel': 'rdf:type'},
                   }

DBPEDIA_MATCHING = '''SELECT ?uri
WHERE{
?uri rdfs:label "%(w)s"@en .
?uri rdf:type ?type
FILTER(?type IN (dbpedia-owl:Agent, dbpedia-owl:Event,
dbpedia-owl:MeanOfTransportation,
dbpedia-owl:Place,
dbpedia-owl:TopicalConcept))
}
'''

ACCEPTABLE_TYPES = set(('http://xmlns.com/foaf/0.1/Person',
                        'http://schema.org/Place',
                        'http://schema.org/Organization',
                        'http://schema.org/Person',
                        'http://www.opengis.net/gml/_Feature',
                        'http://dbpedia.org/class/yago/Person100007846',
                        'http://dbpedia.org/class/yago/LivingPeople',
                        'http://dbpedia.org/ontology/EthnicGroup',
                        'http://dbpedia.org/ontology/MeanOfTransportation',
                        'http://dbpedia.org/ontology/Agent',
                        'http://dbpedia.org/ontology/Place',
                        'http://dbpedia.org/ontology/TopicalConcept',
                        'http://dbpedia.org/ontology/Drug',
                        #'http://dbpedia.org/ontology/Event',
                        #'http://dbpedia.org/ontology/WrittenWork',
                        #'http://umbel.org/umbel/rc/NewspaperSeries',
                        #http://dbpedia.org/ontology/AcademicJournal'
                        ))


def query_dbpedia_match(word):
    results = execute_sparql(DBPEDIA_MATCHING % {'w': word}, 'http://dbpedia.org/sparql')
    return [res['uri']['value'] for res in results]

def query_dbpedia_infos(uri, lang_orders=('fr', 'en')):
    triples = [DBPEDIA_TRIPLES[triple] for triple in ('topic', 'abstract', 'depiction', 'label', 'thumbnail')]
    return execute_and_merge(uri, 'http://dbpedia.org/sparql', triples, lang_orders)


def query_dbpedia_geo_infos(uri, lang_orders=('fr', 'en')):
    triples = [DBPEDIA_TRIPLES[triple] for triple in ('topic', 'abstract', 'depiction',
                                                      'label', 'thumbnail', 'geometry',
                                                      'latitude', 'longitude')]
    results = execute_and_merge(uri, 'http://dbpedia.org/sparql', triples, lang_orders)
    if not results['latitude'] or not results['longitude']:
        return {}
    return results

def query_dbpedia_categories(uri, lang_orders=('fr', 'en')):
    triples = [DBPEDIA_TRIPLES[triple] for triple in ('subject',)]
    query = sparql_query_builder(uri, triples=triples)
    categories = execute_sparql(query, 'http://dbpedia.org/sparql')
    results = []
    triples = [DBPEDIA_TRIPLES[triple] for triple in ('label',)]
    for category in categories:
        uri = category['subject']['value']
        info = execute_and_merge(uri, 'http://dbpedia.org/sparql', triples, lang_orders)
        info['subject'] = uri
        results.append(info)
    return results

def query_dbpedia_is_in_category(uri, lang_orders=('fr', 'en')):
    query =  ("SELECT ?uri\n"
              "WHERE {?uri dcterms:subject  <%(uri)s> .}" % {'uri': uri})
    results = execute_sparql(query, 'http://dbpedia.org/sparql')
    return [res['uri']['value'] for res in results]

def query_dbpedia_types(uri, lang_orders=('fr', 'en')):
    query = '''SELECT ?type WHERE{
    <%s> rdf:type ?type
    }'''
    results = execute_sparql(query % uri, 'http://dbpedia.org/sparql')
    return set([r['type']['value'] for r in results])
