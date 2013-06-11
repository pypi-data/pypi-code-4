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

from cubicweb.selectors import is_instance
from cubicweb.web.views.primary import PrimaryView


class ExternalUriPrimaryView(PrimaryView):
    __select__ = PrimaryView.__select__ & is_instance('ExternalUri')

    def call(self, rset=None):
        entity = self.cw_rset.get_entity(0,0)
        # HEADER
        self.w(u'<div class="page-header">')
        self.w(u'<h1>%s</h1>' % entity.dc_title())
        self.w(u'</div>')
        # FIRST SECTION - INFORMATION
        self.w(u'<div class="well">')
        self.w(u'<div class="row-fluid">')
        # Depiction
        self.w(u'<div class="span3">')
        self.w(u'<a href="#" class="thumbnail"><img src="%s" alt=""></a>' % entity.depiction)
        self.w(u'</div>')
        ### Abstract and links
        self.w(u'<div class="span6">')
        self.w(u'<h4>%s</h4><p>%s</p>' % (self._cw._('Description'), entity.dc_description()))
        for link, label in entity.external_links:
            self.w(u'<p><a href="%s">%s</a></p>' % (link, self._cw._(label)))
        url = self._cw.build_url(rql='Any X WHERE X recognized_entities E, E eid %(e)s' % {'e': entity.eid})
        self.w(u'<a class="btn" href="%s">%s</a>' % (url, self._cw._('See the articles about this subject')))
        self.w(u'</div>')
        # Categories
        self.w(u'<div class="span3">')
        categories = entity.categories
        if categories:
            self.w(u'<h4>%s</h4>' % self._cw._('Categories'))
            self.w(u'<ul>')
            for category in categories:
                if not category['label']:
                    continue
                url = category['subject']
                url = self._cw.build_url('', vid='category-view', category=url)
                self.w(u'<li><a href="%s">%s</a></li>' % (url, category['label']))
            self.w(u'</ul>')
        self.w(u'</div>') # Categories
        self.w(u'</div>') # Row
        self.w(u'</div>') # well
        # SECOND SECTION - RELATED ENTITIES
        self.w(u'<h3>%s</h3>' % self._cw._('Most related entities'))
        rset = entity.related_named_entities(limit=None)
        self.wview('panel', rset=rset, limit=12)
        # Appearances
        self.w(u'<div class="row-fluid">')
        self.w(u'<h3>%s</h3>' % self._cw._('Joint appearances in the News'))
        self.wview('d3-bar-chart', rset=rset.limit(40), minval=2)
        self.w(u'</div>')
        # Frequency
        self.w(u'<div class="row-fluid">')
        self.w(u'<h3>%s</h3>' % self._cw._('Frequency in the News'))
        rset = self._cw.execute('Any X WHERE X recognized_entities E, E eid %(e)s' % {'e': entity.eid})
        self.wview('frequency', rset=rset)
        self.w(u'</div>')


class NewsArticleTweetPrimaryView(PrimaryView):
    __select__ = PrimaryView.__select__ & is_instance('NewsArticle', 'Tweet')

    def call(self, rset=None):
        w = self.w
        entity = self.cw_rset.get_entity(0,0)
        w(u'<div class="page-header">')
        w(u'<h1>')
        w(entity.dc_title())
        date = entity.printable_value('date') or entity.printable_value('creation_date')
        w(u'<br/><small><a href="%s">(%s - %s)</a></small>' % (entity.uri, entity.source[0].name, date))
        w(u'</h1>')
        w(u'</div>')
        w(u'<div class="well">')
        w(u'<div class="row-fluid">')
        # Content
        w(u'<div class="span9">')
        content = entity.preview_content
        if content:
            w(u'<h3>%s</h3>' % self._cw._('Content preview'))
            w(u'<p>%s</p>' % content)
            w(u'<a class="btn btn-primary" href="%s">%s</a>' % (entity.uri, self._cw._('See full content')))
        ner_rset = entity.named_entities
        if ner_rset:
            w(u'<h3>%s</h3>' % self._cw._('Recognized entities'))
            self.wview('panel', rset=ner_rset, limit=None)
        w(u'</div>')
        # Categories/HashTags
        w(u'<div class="span3">')
        categories = entity.categories
        if categories:
            w(u'<h4>%s</h4>' % self._cw._(entity.category_label))
            w(u'<ul>')
            for category in categories:
                self.w(u'<li><a href="%s">%s</a></li>' % (category.absolute_url(), category.dc_title()))
            self.w(u'</ul>')
        w(u'</div>')
        w(u'</div>') # Row
        w(u'</div>') # well
