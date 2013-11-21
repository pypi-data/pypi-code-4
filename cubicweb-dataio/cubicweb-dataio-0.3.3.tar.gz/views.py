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

"""cubicweb-dataio views/forms/actions/components for web ui"""
from logilab.common.decorators import monkeypatch

from cubicweb.web import Redirect
from cubicweb.web import controller
from cubicweb.web import component

from cubes.dataio.xy import XY

try:
    from fyzz.yappsparser import parse
    from fyzz import ast
    from cubicweb import spa2rql
    fyzz_imported = True
except ImportError:
    fyzz_imported = False

try:
    import rdflib
except ImportError:
    rdflib = None


###############################################################################
### RDF VIEW ##################################################################
###############################################################################
if rdflib is not None:

    from rdflib import Literal, URIRef
    from cubicweb.web.views.rdf import RDFView, RDF

    from cubes.dataio.xy import XY as xy


    class DataIORDFView(RDFView):

        def call(self):
            graph = rdflib.Graph()
            # Call dataio xy prefixes
            for prefix, xmlns in xy.prefixes.items():
                graph.bind(prefix, rdflib.Namespace(xmlns))
            for i in xrange(self.cw_rset.rowcount):
                entity = self.cw_rset.complete_entity(i, 0)
                self.entity2graph(graph, entity)
            format = self._cw.form.get('__format', 'xml')
            self.w(graph.serialize(format=format).decode('utf-8'))

        @property
        def content_type(self):
            format = self._cw.form.get('__format', 'xml')
            if format == 'xml':
                return 'application/rdf+xml'
            elif format == 'n3':
                # cf. http://www.w3.org/TeamSubmission/n3/#hist_mime
                return 'text/n3'
            else: # i.e. 'nt'
                # http://www.w3.org/TR/rdf-testcases/#ntriples says
                # "The Internet media type / MIME type of N-Triples is text/plain"
                return 'text/plain'

        def entity2graph(self, graph, entity):
            add = graph.add
            etype = entity.e_schema.type
            cwuri = URIRef(entity.cwuri)
            # Add etype
            for obj in xy.etype_to_rdf(etype):
                add( (cwuri, RDF.type, URIRef(obj)) )
            # Add attributes/relations
            for subj, rel, obj, _type in xy.iter_entity_triples(entity):
                if _type == 'literal':
                    add((URIRef(cwuri), URIRef(rel), Literal(obj)))
                else:
                    add((URIRef(cwuri), URIRef(rel), URIRef(obj)))


###############################################################################
### SPARQL2RQL TRANSLATOR #####################################################
###############################################################################
if fyzz_imported:
    @monkeypatch(spa2rql.Sparql2rqlTranslator)
    def translate(self, sparql):
        sparqlst = parse(sparql)
        if sparqlst.type != 'select':
            raise spa2rql.UnsupportedQuery()
        qi = spa2rql.QueryInfo(sparqlst)
        for subj, predicate, obj in sparqlst.where:
            if not isinstance(subj, ast.SparqlVar):
                raise UnsupportedQuery()
            # make a valid rql var name
            subjvar = subj.name.upper()
            if predicate in [('', 'a'),
                             ('http://www.w3.org/1999/02/22-rdf-syntax-ns#', 'type')]:
                # special 'is' relation
                if not isinstance(obj, tuple):
                    raise UnsupportedQuery()
                # restrict possible types for the subject variable
                qi.set_possible_types(
                    subjvar, XY.yeq(':'.join(obj), isentity=True))
            else:
                # 'regular' relation (eg not 'is')
                if not isinstance(predicate, tuple):
                    raise UnsupportedQuery()
                # list of 3-uple
                #   (yams etype (subject), yams rtype, yams etype (object))
                # where subject / object entity type may '*' if not specified
                yams_predicates = XY.yeq(':'.join(predicate))
                qi.infer_types_info.append((yams_predicates, subjvar, obj))
                if not isinstance(obj, (ast.SparqlLiteral, ast.SparqlVar)):
                    raise spa2rql.UnsupportedQuery()
        qi.infer_types()
        qi.build_restrictions()
        return qi


###############################################################################
### SPARQL COMPONENT ##########################################################
###############################################################################
class SparqlInputForm(component.Component):
    __regid__ = 'sparqlinput'
    visible = True

    def call(self, view=None):
        req = self._cw
        self.w(u'''<div id="sparqlinput"><form action="%s">
        <fieldset>
        <textarea id="sparql" name="sparql" value="" accesskey="q"></textarea>
        </fieldset>
        <button type="submit" value="sparqxml" name="format" class="btn">xml</button>
        <button type="submit" value="table" name="format" class="btn">table</button>
        </form></div>'''% req.build_url('sparql-results'))


class SimpleUiSparqlController(controller.Controller):
    __regid__ = 'sparql-results'

    def publish(self, rset=None):
        sparql_query = self._cw.form.get('sparql')
        sparql_format = self._cw.form.get('format', 'table')
        if sparql_query:
            try:
                qinfo = spa2rql.Sparql2rqlTranslator(self._cw.vreg.schema).translate(sparql_query)
            except:
                raise Redirect(self._cw.build_url())
            rql, args = qinfo.finalize()
            url = self._cw.build_url('view', rql=rql % args, vid=sparql_format)
            raise Redirect(url)
        raise Redirect(self._cw.build_url())


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, (DataIORDFView,))
    if rdflib is not None:
        vreg.register_and_replace(DataIORDFView, RDFView)
    # Register parser
    from cubes.dataio.datafeed import SparqlParser
    vreg.register(SparqlParser)
