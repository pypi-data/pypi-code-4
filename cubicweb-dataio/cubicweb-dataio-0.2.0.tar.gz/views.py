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

try:
    import rdflib
except ImportError:
    rdflib = None

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


    def registration_callback(vreg):
        vreg.register_and_replace(DataIORDFView, RDFView)
