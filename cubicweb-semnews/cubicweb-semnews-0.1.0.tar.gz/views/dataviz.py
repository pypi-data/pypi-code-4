
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

"""cubicweb-semnews views/forms/actions/components for web ui"""
from cubicweb.utils import json_dumps

from cubicweb.predicates import is_instance
from cubicweb.view import EntityView


###############################################################################
### D3 JS VIEWS ###############################################################
###############################################################################
class D3BundlingWheelView(EntityView):
    __regid__ = 'd3-wheel'
    __select__ = EntityView.__select__ & is_instance('ExternalUri')

    def call(self, **kwargs):
        _id = 'wheel'
        self.w(u'<div id="%s"/>' % _id)
        entities = {}
        for entity in self.cw_rset.entities():
            entities[entity.eid] = ({'label':  entity.dc_title(),
                                    'url': entity.absolute_url(),
                                    'depiction': entity.depiction,
                                    'weight': len(entity.reverse_recognized_entities),
                                    'id': entity.eid},
                                    entity)
        graph = {}
        for eid, (data, entity) in entities.iteritems():
            edges = set([(r[0], r[1]) for r in entity.related_named_entities(limit=None)
                         if (r[0] != eid and r[0] in entities)])
            data['edges'] = list(edges)
            if data['edges']:
                graph[eid] = data
        graph = json_dumps(graph)
        self._cw.add_onload('cw.cubes.semnews.d3BundlingWheel(%s, "wheel")' % graph)
        self.w(u'</div>')
        self.w(u'</div>')


class D3BarChartView(EntityView):
    __regid__ = 'd3-bar-chart'

    def call(self, minval=None, **kwargs):
        self.w(u'<div id="bar-chart"/>')
        data = []
        for entity in self.cw_rset.entities():
            value = len(entity.reverse_recognized_entities)
            if minval and value<minval:
                continue
            data.append({'label': entity.dc_title(),
                         'url': entity.absolute_url(),
                         'value': value,})
        data = [d for d in sorted(data, reverse=True, key=lambda x: x['value'])]
        data = json_dumps(data)
        self._cw.add_onload('cw.cubes.semnews.d3BarChart(%s, "bar-chart")' % data)


class FrequencyView(EntityView):
    __regid__ = 'frequency'
    __select__ = EntityView.__select__ & is_instance('NewsArticle', 'Tweet')

    def call(self):
        _id = 'bar-frequency'
        self.w(u'<div id="%s"/>' % _id)
        counts = {}
        for month, day in self._cw.execute('DISTINCT Any MONTH(C), DAY(C) WHERE X creation_date C, '
                                           'X is IN (NewsArticle, Tweet)'):
            key = (month, day)
            counts.setdefault(key, [])
        for e in self.cw_rset.entities():
            cd = e.creation_date
            key = (cd.month, cd.day)
            counts[key].append(e.eid)
        data = []
        for k, v in sorted(counts.iteritems()):
            data.append({'label':  '%s/%s' % k, 'value': len(v)})
        data = json_dumps(data)
        self._cw.add_onload('cw.cubes.semnews.d3BarChart(%s, "%s")' % (data, _id))
