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

from unicodedata import category
from datetime import datetime
from collections import defaultdict
import os.path as osp
import re
import io
try:
    import rdflib
    rdlib_available = True
except:
    rdlib_available = False
try:
    import RDF
    librdf_available = True
except:
    librdf_available = False

from cubicweb.dataimport import ucsvreader


###############################################################################
### GLOBAL VARIABLES ##########################################################
###############################################################################
LIBRDF_FORMATS_MAPPING = {'ntriples': 'ntriples',
                          'nt': 'ntriples',
                          'n3': 'turtle',
                          'xml': 'rdfxml',
                          'rdf': 'rdfxml',
                          'xml/rdf': 'rdfxml',
                          'rdfxml': 'rdfxml'}

RDFLIB_FORMATS_MAPPING = {'ntriples': 'nt',
                          'n3': 'n3',
                          'nt': 'nt',
                          'xml': 'xml',
                          'rdf': 'xml',
                          'xml/rdf': 'xml',
                          'rdfxml': 'xml'}

SEPARATOR_MAPPING = {'space': ' ', 'comma': ',', 'tab': '\t'}

DEFAULT_NAMESPACE = 'http://ns.cubicweb.org/cubicweb/0.0/'

NAMESPACES = {
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'foaf': 'http://xmlns.com/foaf/0.1/',
    'xfoaf': 'http://www.foafrealm.org/xfoaf/0.1/',
    'dcmitype': 'http://purl.org/dc/dcmitype/',
    'ore': 'http://www.openarchives.org/ore/terms/',
    'dbpedia': 'http://dbpedia.org/',
    'dbpediaowl': 'http://dbpedia.org/ontology/',
    'dbprop': 'http://dbpedia.org/property/',
    'rdagroup2elements': 'http://RDVocab.info/ElementsGr2/',
    'frbr': 'http://rdvocab.info/uri/schema/FRBRentitiesRDA/',
    'rdarole': 'http://rdvocab.info/roles/',
    'rdagroup1elements': 'http://RDVocab.info/Elements/',
    'rdarelationships': 'http://rdvocab.info/RDARelationshipsWEMI/',
    'og': 'http://ogp.me/ns#',
    'bnf-onto': 'http://data.bnf.fr/ontology/',
    'dc': 'http://purl.org/dc/terms/',
    'owl': 'http://www.w3.org/2002/07/owl#',
    'geo': 'http://www.w3.org/2003/01/geo/wgs84_pos#',
    'cc': 'http://creativecommons.org/ns#',
    'swvs': 'http://www.w3.org/2003/06/sw-vocab-status/ns#',
    'cw': 'http://ns.cubicweb.org/cubicweb/0.0/',
    }

REVERSE_NAMESPACES = dict([(v,k) for k,v in NAMESPACES.items()])

NAME_START_CATEGORIES = ["Ll", "Lu", "Lo", "Lt", "Nl"]
NAME_CATEGORIES = NAME_START_CATEGORIES + ["Mc", "Me", "Mn", "Lm", "Nd"]
ALLOWED_NAME_CHARS = [u"\u00B7", u"\u0387", u"-", u".", u"_"]
XMLNS = "http://www.w3.org/XML/1998/namespace"

# Rdf property used to store uri
URI_RDF_PROP = u'http://www.w3.org/1999/02/22-rdf-syntax-ns#about'


################################################################################
### READER CLASS ###############################################################
################################################################################
class AbstractRdfReader(object):
    """ Abstract class for reader """

    def __init__(self, rdf_format=None, _encoding='utf-8'):
        self.rdf_format = rdf_format
        self._encoding = _encoding

    def iterate_triples_from_file(self, filename):
        """ Iterate triples over the given file
        """
        with open(filename) as fobj:
            for data in self.iterate_triples(fobj):
                yield data

    def iterate_triples(self, fobj):
        """ Iterate triples over the given file
        """
        raise NotImplementedError()


class RawNtRdfReader(AbstractRdfReader):
    """ Raw nt reader class"""
    BASE_RESOURCE_REGEXP = r'^<(.*)>\s+<(.*)>\s+<(.*)>\s*.\s*$'
    BASE_LITERAL_REGEXP = r'^<(.*)>\s+<(.*)>\s+"(.*)"(?:\@.*)*\s*.\s*'

    def __init__(self, resource_regexp=None, literal_regexp=None, _encoding='utf-8'):
        """ Init the Raw nt rdf reader, with an encoding, a resource regexp and a literal regexp.
        If none, choose the base regexps """
        resource_regexp = resource_regexp or self.BASE_RESOURCE_REGEXP
        literal_regexp = literal_regexp or self.BASE_LITERAL_REGEXP
        super(RawNtRdfReader, self).__init__(_encoding=_encoding)
        self.literal_regexp = re.compile(literal_regexp)
        self.resource_regexp = re.compile(resource_regexp)

    def iterate_triples(self, fobj):
        """ Iterate triples using rawnt format (e.g. from split function)
        """
        for line in fobj:
            data = []
            match = self.resource_regexp.match(line)
            if match:
                data = [m.decode(self._encoding) for m in match.groups()]
                data.append('resource')
                yield tuple(data)
                continue
            match = self.literal_regexp.match(line)
            if match:
                data = [m.decode(self._encoding) for m in match.groups()]
                data.append('literal')
                yield tuple(data)


class LibRdfReader(AbstractRdfReader):
    """ Lib RDF reader class"""

    def __init__(self, rdf_format='rdfxml', _encoding='utf-8'):
        """ Init the LibRDF reader, with a rdf format (default is 'rdfxml')
        """
        rdf_format = LIBRDF_FORMATS_MAPPING.get(rdf_format, rdf_format)
        super(LibRdfReader, self).__init__(rdf_format=rdf_format,
                                           _encoding=_encoding)

    def iterate_triples_from_file(self, filename):
        """ Iterate triples over the given file
        """
        parser = RDF.Parser(name=self.rdf_format)
        stream = parser.parse_as_stream('file://' + osp.realpath(filename))
        for data in self.iterate_triples(stream):
            yield data

    def iterate_triples(self, stream):
        """ Iterate triples using librdf
        """
        for triple in stream:
            _subject = unicode(triple.subject.uri)
            _predicate = unicode(triple.predicate.uri)
            if triple.object.is_resource():
                otype = u'resource'
                _object = unicode(triple.object.uri)
            else:
                otype = u'literal'
                _object = unicode(triple.object.literal_value['string'])
            yield _subject, _predicate, _object, otype


class RdfLibReader(AbstractRdfReader):

    def __init__(self, rdf_format='xml', _encoding='utf-8'):
        """ Init the RDFLib reader, with a rdf format (default is 'rdfxml')
        """
        rdf_format = RDFLIB_FORMATS_MAPPING.get(rdf_format, rdf_format)
        super(RdfLibReader, self).__init__(rdf_format=rdf_format,
                                           _encoding=_encoding)

    def iterate_triples(self, fobj):
        """ Iterate triples using rdflib
        """
        rdfgraph = rdflib.ConjunctiveGraph()
        rdfgraph.parse(fobj, format=self.rdf_format)
        for _subject, _predicate, _object in rdfgraph:
            if isinstance(_object, rdflib.URIRef):
                otype = 'resource'
            else:
                otype = 'literal'
            _object = _object.format()
            yield unicode(_subject.format()), unicode(_predicate), _object, otype


class CSVRdfReader(AbstractRdfReader):
    """ CSV reader mimicing RDF """

    def __init__(self, fields=None, _encoding='utf-8'):
        """ Init the RDFLib reader, with a rdf format (default is 'rdfxml')
        """
        super(CSVRdfReader, self).__init__(_encoding=_encoding)
        self.fields = fields or {}

    def iterate_triples_from_file(self, filename, separator=',',
                                  null_value='NULL',
                                  uri_ind=None, _header=0,
                                  limit=None, ignore_errors=False):
        """ Iterate triples over the given file
        """
        if separator in SEPARATOR_MAPPING:
            separator = SEPARATOR_MAPPING[separator]
        fobj = ucsvreader(open(filename), separator=separator,
                          ignore_errors=ignore_errors)
        for data in self.iterate_triples(fobj, uri_ind=uri_ind,
                                         null_value='NULL',
                                         _header=_header, limit=limit):
            yield data

    def iterate_triples(self, fobj, uri_ind=None, null_value='NULL', _header=0, limit=None):
        """ Iterate triples using librdf
        """
        for ind, row in enumerate(fobj):
            #XXX We should take care from line skipping, because ucsvreader() with
            #    ignore_errors=True already skips the first line !
            if _header and ind < _header:
                continue
            if limit and ind > limit:
                break
            _subject = row[uri_ind] if uri_ind is not None else 'line %s' % ind
            for row_ind, _object in enumerate(row):
                # Keep value if no mapping or row indice in mapping
                if not self.fields:
                    _predicate = 'row %s' % row_ind
                elif self.fields and row_ind in self.fields:
                    _predicate = self.fields[row_ind]
                else:
                    continue
                if _object != null_value:
                    otype = 'literal' if not _object.startswith('http') else 'resource'
                    yield _subject, _predicate, _object, otype



################################################################################
### WRITER CLASS  ##############################################################
################################################################################
class AbstractRdfWriter(object):
    """ Abstract class for writer """

    def __init__(self, _encoding='utf-8'):
        self.triples_counter = 0
        self.graph = None
        self._encoding = _encoding
        self._init_graph()

    def _init_graph(self):
        """ Init a empty graph
        """
        raise NotImplementedError()

    def add_triple(self, _s, _p, _o, _ot):
        """ Add a triple to the current graph
        """
        self.triples_counter += 1

    def autodetect_type(self, _o, _ot=None):
        """ Try to autodetect data type
        """
        if _ot:
            return _ot
        return 'literal' if not _o.startswith('http') else 'resource'

    def write(self, buff, rdf_format=None):
        """ Write the graph into a given file-like buffer
        """
        raise NotImplementedError()

    def write_file(self, filename, rdf_format=None):
        """ Write the graph into the given file
        """
        with open(filename, 'w') as fobj:
            self.write(fobj, rdf_format)


class RawNtRdfWriter(AbstractRdfWriter):
    """ Raw nt writer class"""

    def _init_graph(self):
        self.graph = []

    def add_triple(self, _s, _p, _o, _ot=None):
        super(RawNtRdfWriter, self).add_triple(_s, _p, _o, _ot)
        _ot = self.autodetect_type(_o, _ot)
        if _ot == 'literal':
            self.graph.append(u'<%s> <%s> "%s" .' % (_s, _p, _o))
        if _ot == 'resource':
            self.graph.append(u'<%s> <%s> <%s> .' % (_s, _p, _o))

    def write(self, buff, rdf_format=None):
        if self.graph:
            buff.write('\n'.join(self.graph).encode(self._encoding))


class LibRdfWriter(AbstractRdfWriter):
    """ LibRDF writer class"""

    def __init__(self, xy=None, _encoding='utf-8'):
        self.xyreg = xy
        super(LibRdfWriter, self).__init__(_encoding)

    def _init_graph(self):
        self.graph = RDF.Model()

    def add_triple(self, _s, _p, _o, _ot=None):
        super(LibRdfWriter, self).add_triple(_s, _p, _o, _ot)
        _ot = self.autodetect_type(_o, _ot)
        if _ot == 'resource':
            _o = RDF.Uri(_o.encode(self._encoding))
        else:
            _o = _o.encode(self._encoding)
        self.graph.append(RDF.Statement(RDF.Uri(_s.encode(self._encoding)),
                                        RDF.Uri(_p.encode(self._encoding)),
                                        _o))

    def write(self, buff, rdf_format=None):
        rdf_format = LIBRDF_FORMATS_MAPPING.get(rdf_format, 'rdfxml')
        serializer = RDF.Serializer(name=rdf_format)
        if self.xyreg:
            for rdfns, vocab in self.xyreg.reverse_ns.iteritems():
                serializer.set_namespace(vocab, rdfns)
        buff.write(serializer.serialize_model_to_string(self.graph))


class RdfLibWriter(AbstractRdfWriter):
    """ RDFLib writer class"""

    def __init__(self, xy=None, _encoding='utf-8'):
        self.xyreg = xy
        super(RdfLibWriter, self).__init__(_encoding)

    def _init_graph(self):
        self.graph = rdflib.ConjunctiveGraph()
        if self.xyreg:
            for rdfns, vocab in self.xyreg.reverse_ns.iteritems():
                self.graph.bind(vocab, rdfns)

    def add_triple(self, _s, _p, _o, _ot=None):
        super(RdfLibWriter, self).add_triple(_s, _p, _o, _ot)
        _ot = self.autodetect_type(_o, _ot)
        if _ot == 'resource':
            _o = rdflib.URIRef(_o.encode(self._encoding))
        else:
            _o = rdflib.Literal(_o.encode(self._encoding))
        self.graph.add((rdflib.URIRef(_s), rdflib.URIRef(_p), _o))

    def write(self, buff, rdf_format=None):
        rdf_format = RDFLIB_FORMATS_MAPPING.get(rdf_format, 'xml')
        buff.write(self.graph.serialize(format=rdf_format))
        self.graph.close()


class CSVRdfWriter(AbstractRdfWriter):
    """ CSV writer mimicing RDF """

    def __init__(self, separator=',', null_value='NULL', _encoding='utf-8'):
        self.separator = ','
        self.null_value = null_value
        super(CSVRdfWriter, self).__init__(_encoding)

    def _init_graph(self):
        self.graph = defaultdict(dict)
        self.fields = set()

    def add_triple(self, _s, _p, _o, _ot=None):
        super(CSVRdfWriter, self).add_triple(_s, _p, _o, _ot)
        _o.encode(self._encoding)
        self.graph[_s][_p] = _o
        self.fields.add(_p)

    def write(self, buff, rdf_format=None):
        fields = list(self.fields)
        for uri, objects in self.graph.iteritems():
            data = [uri,]
            for field in fields:
                data.append(objects.get(field, self.null_value))
            buff.write(self.separator.join(data).encode(self._encoding)+'\n')


################################################################################
### UTILITY FUNCTIONS ##########################################################
################################################################################
def build_rdf_reader(library='rdflib', rdf_format='xml', _encoding='utf-8'):
    """ Build a reader object, given a library, a rdf_format and _encoding
    Possible libraries are 'rdflib', 'librdf' and 'rawnt' """
    if library == 'rdflib':
        if rdlib_available:
            return RdfLibReader(rdf_format, _encoding=_encoding)
        else:
            raise NotImplementedError('rdflib does not seems to be available.')
    elif library == 'librdf':
        if librdf_available:
            return LibRdfReader(rdf_format, _encoding=_encoding)
        else:
            raise NotImplementedError('librdf does not seems to be available.')
    elif library == 'rawnt':
        return RawNtRdfReader(_encoding=_encoding)
    else:
        raise NotImplementedError('Unknown library: should be rdflib, librdf '
                                  'or rawnt')

def build_rdf_writer(library='rdflib', _encoding='utf-8', xy=None):
    """ Build a writer object, given a library, and an xy object
    Possible libraries are 'rdflib', 'librdf' and 'rawnt' """
    if library == 'rdflib':
        return RdfLibWriter(xy=xy, _encoding=_encoding)
    elif library == 'librdf':
        return LibRdfWriter(xy=xy, _encoding=_encoding)
    elif library == 'rawnt':
        return RawNtRdfWriter(_encoding=_encoding)
    else:
        raise NotImplementedError('Unknown library: should be rdflib, librdf '
                                  'or rawnt')


###############################################################################
### CONVERTER FUNCTIONS #######################################################
###############################################################################
def convert_string(_object,  **kwargs):
    """ Convert an rdf value to a String """
    return _object

def convert_int(_object, **kwargs):
    """ Convert an rdf value to an int """
    try:
        return int(_object)
    except:
        return None

def convert_float(_object, **kwargs):
    """ Convert an rdf value to a float """
    try:
        return float(_object.replace(',', '.'))
    except:
        return None

def convert_date(_object, datetime_format='%d-%m-%Y', **kwargs):
    """ Convert an rdf value to a date """
    try:
        return datetime.strptime(_object, datetime_format)
    except:
        return None

def convert_geo(_object, **kwargs):
    """ Convert an rdf value to a geo
    XXX GEO DOES NOT EXIST FOR NOW IN YAMS
    """
    try:
        # XXX Bad conversion
        _object = _object.replace(' ', '').replace("'", '').replace(u'°', '.').strip().lower()
        if not _object.isdigit():
            for a in ascii_lowercase:
                _object = _object.replace(a, '')
            _object = _object.strip()
        return float(_object)
    except:
        return None

DEFAULT_CONVERTERS = {'String': convert_string,
                      'Int': convert_int, 'BigInt': convert_int,
                      'Float': convert_float, 'Date': convert_date,
                      'Geo': convert_geo}


###############################################################################
### RDF UTILITY FUNCTIONS #####################################################
###############################################################################
def normalize_xml(uri, namespaces=REVERSE_NAMESPACES):
    """ Return an clean RDF node from an uri, e.g.
    http://rdvocab.info/uri/schema/FRBRentitiesRDA/Manifestation -> rdf:Manifestation
    """
    uri_ns, uri_part = split_uri(uri)
    return ':'.join([namespaces.get(uri_ns, uri_ns), uri_part])

def split_uri(uri):
    """ Split an uri between the namespace and the property, ie.
    http://rdvocab.info/uri/schema/FRBRentitiesRDA/Manifestation
    ->
    (http://rdvocab.info/uri/schema/FRBRentitiesRDA/ , Manifestation)

    This is a backport from rdflib, as we don't want a hard dependancy on it
    """
    if uri.startswith(XMLNS):
        return (XMLNS, uri.split(XMLNS)[1])
    length = len(uri)
    uri = unicode(uri)
    for i in xrange(0, length):
        c = uri[-i-1]
        if not category(c) in NAME_CATEGORIES:
            if c in ALLOWED_NAME_CHARS:
                continue
            for j in xrange(-1-i, length):
                if category(uri[j]) in NAME_START_CATEGORIES or uri[j]=="_":
                    ns = uri[:j]
                    if not ns:
                        break
                    ln = uri[j:]
                    return (ns, ln)
            break
    raise Exception("Can't split '%s'" % uri)

def build_uri_dict(filenames, library='librdf', rdf_format='xml', _encoding='utf-8', limit=None):
    """ Build a dictionnary (ns:part, (predicate, object)) for each uri, from an rdf file """
    rdf_reader = build_rdf_reader(library=library, rdf_format=rdf_format, _encoding=_encoding)
    # Construct the URI dictionnary
    uri_dictionnary = {}
    count = 0
    for filename in filenames:
        # Use iterate_triples_from_file for good handling of librdf
        for uri, _predicate, _object, _type in rdf_reader.iterate_triples_from_file(filename):
            uri_dictionnary.setdefault(uri, {})[URI_RDF_PROP] = [(uri, 'resource'),]
            uri_dictionnary[uri].setdefault(_predicate, []).append((_object,_type))
            count += 1
            if limit and count>limit:
                break
        if limit and count>limit:
            break
    return uri_dictionnary


###############################################################################
### FILE UTILITY FUNCTIONS ####################################################
###############################################################################
class DictFobj(object):
    """ Class for file-based dictionnary, use for large file conversion based
    on a mapping.
    Learn the mapping (index, offset), where the key of interest
    is given by its value in the splitted line (index_key).
    The mapping gets, for a key, the offset in the file, and store it in an internal dict.
    It will re-read the line of corresponding offset on get() and return the
    line splitted on the separator (i.e. a list)

    >>>  filename = osp.join(HERE, 'data/mmap.csv')
    >>>  mmap = DictFobj(filename, separator=',', cast_type=int)
    >>>  mmap.fit()
    >>>  print mmap.get(1)[1]
    'Toto'

    """

    def __init__(self, fname, separator='\t', cast_type=None):
        """ Class for file-based dictionnary, use for large file conversion based
        on a mapping.

        fname: name of the file
        separator: separator of the csv file
        cast_type: cast callback for the key of the dictionnary (e.g. int)
        """
        self.fname = fname
        self.fobj = io.open(self.fname, 'rb', buffering=0)
        self.separator = separator
        self.cast_type = cast_type
        self.internal_dict = {}

    def __del__(self):
        self.fobj.close()

    def fit(self, index_key=0):
        """ Learn the mapping (index, offset), where the key of interest
        is given by its value in the splitted line (index_key).
        The mapping gets, for a key, the offset in the file, and store it in an internal dict
        """
        self.fobj.seek(0)
        pos = self.fobj.tell()
        while True:
            # Read the line
            line = self.fobj.readline()
            if not line:
                break
            # Get the key of the line (and eventually cast it)
            key = line.split(self.separator)[index_key]
            if self.cast_type:
                key = self.cast_type(key)
            # Store the result in an internal dict
            self.internal_dict[key] = pos
            pos = self.fobj.tell()

    def get(self, key):
        """Re-read the line of corresponding offset on get() and return the
        line splitted on the separator (i.e. a list)"""
        pos = self.internal_dict.get(key)
        if pos is None:
            return
        self.fobj.seek(pos)
        line = self.fobj.readline()
        return line.strip().split(self.separator)

