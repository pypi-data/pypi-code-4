# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
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
from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance
from cubicweb.view import EntityView


###############################################################################
### EXTERNAL URIS #############################################################
###############################################################################
class ExternalUriOutOfContextView(EntityView):
    __regid__ = 'outofcontext'
    __select__ = EntityView.__select__ & is_instance('ExternalUri')

    def cell_call(self, row, col, trend=True):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div class="row">')
        # Depiction
        self.w(u'<div class="span3">')
        self.w(u'<a href="#" class="thumbnail"><img src="%s" alt=""></a>' % entity.depiction)
        self.w(u'</a>')
        self.w(u'</div>')
        # General infos
        self.w(u'<div class="span7">')
        self.w(u'<h4><a href="%s">%s</a></h4>' % (entity.absolute_url(), entity.dc_title()))
        self.w(u'</div>')
        # Trends
        if trend:
            self.w(u'<div class="span2">')
            self.w(u'<img src="%s"/>' % entity.trend_logo())
            self.w(u'</div>')
        self.w(u'</div>')


class ExternalUriPanelView(EntityView):
    __regid__ = 'panel'
    __select__ = EntityView.__select__ & is_instance('ExternalUri')

    def call(self, rset=None, limit=12):
        rset = rset or self.cw_rset
        if limit:
            entities = list(rset.entities())[:limit]
        else:
            entities = list(rset.entities())
        nb_row = len(rset)/4 or 1
        for ind_row in range(nb_row):
            self.w(u'<div class="row-fluid">')
            for _entity in entities[ind_row*4:(ind_row+1)*4]:
                self.w(u'<div class="span3">%s</div>' % _entity.view('outofcontext', trend=False))
            self.w(u'</div>')


###############################################################################
### NEWS ARTICLES AND TWEETS ##################################################
###############################################################################
class NewsArticleOutOfContextView(EntityView):
    __regid__ = 'outofcontext'
    __select__ = EntityView.__select__ & is_instance('NewsArticle')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div>')
        self.w(u'<h4><a href="%s">%s</a></h4>' % (entity.absolute_url(), entity.dc_title()))
        content = entity.preview_content
        if content:
            self.w(u'<p>%s</p>' % content)
        self.w(u'</div>')


class TweetOutOfContextView(EntityView):
    __regid__ = 'outofcontext'
    __select__ = EntityView.__select__ & is_instance('Tweet')

    def cell_call(self, row, col):
        entity = self.cw_rset.get_entity(row, col)
        self.w(u'<div>')
        self.w(u'<h4><a href="%s">%s - "%s"</a></h4>'
               % (entity.absolute_url(), self._cw._('Tweet'), entity.source[0].url))
        self.w(u'<p>%s</p>' % entity.dc_title())
        self.w(u'</div>')
