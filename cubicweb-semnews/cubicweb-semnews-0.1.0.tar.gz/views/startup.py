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
import urllib

from cubicweb.web.views.startup import IndexView, StartupView

from cubes.semnews.entities.external_resources import query_dbpedia_infos, query_dbpedia_is_in_category


class SemnewsIndexView(IndexView):

    def call(self, day_range=3, lang='fr', limit=40, limit_trend=12):
        lang = self._cw.form.get('__lang') or self._cw.vreg.config['articles-lang'] or lang
        limit = self._cw.form.get('__limit') or self._cw.vreg.config['articles-dataviz-limit'] or limit
        day_range = (self._cw.form.get('__day_range')
                     or self._cw.vreg.config['startup-day-limit'] or day_range)
        limit_trend = (self._cw.form.get('__limit_trend')
                       or self._cw.vreg.config['startup-influent-limit'] or limit_trend)
        rset = self._cw.execute('Any E, COUNT(X) GROUPBY E ORDERBY 2 DESC LIMIT %s '
                                'WHERE X recognized_entities E, E activated TRUE, '
                                'X source S, S lang %%(lg)s, X creation_date D HAVING D > (TODAY - %%(d)s)'
                                % limit, {'lg': lang, 'd': day_range})
        # HTML
        self.w(u'<div class="container">')
        card = self._cw.execute('Any X WHERE X is Card, X title %(t)s', {'t': 'index'})
        if card:
            self.w(card.get_entity(0,0).content)
        # OTHER INFORMATIONS
        self.w(u'<div class="row-fluid">')
        # Most influent entities
        self.w(u'<div class="span4 well">')
        limit_trend = int(self._cw.form.get('__limit_trend', limit_trend))
        if rset:
            self.w(u'<h3>%s</h3>' % self._cw._('Most influent entities'))
            self.wview('list', rset=rset.limit(limit=limit_trend), subvid='outofcontext',
                       klass='list-striped', trend=True)
        self.w(u'</div>')
        # Statistics and wheel
        self.w(u'<div class="span8">')
        if rset:
            self.w(u'<div class="row-fluid">')
            self.w(u'<div class="span10">')
            self.w(u'<h3>%s</h3>' % self._cw._('Relations in the News'))
            self.wview('d3-wheel', rset=rset, lang=lang)
            self.w(u'</div>')
            self.w(u'<div class="span10">')
            self.w(u'<h3>%s</h3>' % self._cw._('Statistics in the News'))
            self.wview('d3-bar-chart', rset=rset.limit(limit/2))
            self.w(u'</div>')
        self.w(u'</div>')
        self.w(u'</div>') # row
        # Close html
        self.w(u'</div>') # container


class CategoryView(StartupView):
    __regid__ = 'category-view'

    def call(self):
        category = self._cw.form.get('category')
        if not category:
            return
        results = query_dbpedia_is_in_category(category)
        if not results:
            return
        uris = ', '.join(['"%s"' % urllib.unquote(uri) for uri in results])
        rset = self._cw.execute('Any X, COUNT(N) GROUPBY X ORDERBY 2 DESC WHERE X is ExternalUri, '
                                'N recognized_entities X, X uri IN (%s)' % uris)
        if rset:
            self.w(u'<div class="row-fluid">')
            self.w(u'<div class="page-header">')
            self.w(u'<h1>%s</h1>' % category)
            self.w(u'</div>')
            self.wview('d3-bar-chart', rset=rset)
            self.w(u'</div>')
            self.w(u'<div class="row-fluid">')
            self.wview('panel', rset=rset, limit=None)
            self.w(u'</div>')


def registration_callback(vreg):
    vreg.register(CategoryView)
    vreg.register_and_replace(SemnewsIndexView, IndexView)
    from cubes.orbui.views.orbui_components import (ApplLogoOrbui,
                                                BreadCrumbEntityVComponentOrbui,
                                                BreadCrumbAnyRSetVComponentOrbui,
                                                BreadCrumbETypeVComponentOrbui)
    vreg.unregister(ApplLogoOrbui)
    vreg.unregister(BreadCrumbEntityVComponentOrbui)
    vreg.unregister(BreadCrumbAnyRSetVComponentOrbui)
    vreg.unregister(BreadCrumbETypeVComponentOrbui)
