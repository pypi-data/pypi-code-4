"""Specific views for links

:organization: Logilab
:copyright: 2003-2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""
__docformat__ = "restructuredtext en"
_ = unicode

from logilab.mtconverter import xml_escape

from cubicweb.predicates import is_instance, one_line_rset
from cubicweb.view import EntityView
from cubicweb.web import formwidgets
from cubicweb.web import action
from cubicweb.web.views import uicfg, primary, baseviews, xbel, bookmark


for attr in ('title', 'url'):
    uicfg.primaryview_section.tag_attribute(('Link', attr), 'hidden')

uicfg.autoform_field_kwargs.tag_attribute(('Link', 'url'),
                                          {'widget': formwidgets.TextInput})


class LinkPrimaryView(primary.PrimaryView):
    __select__ = is_instance('Link')
    show_attr_label = False

    def render_entity_title(self, entity):
        title = u'<a href="%s">%s</a>' % (xml_escape(entity.url),
                                          xml_escape(entity.title))
        self.w(u'<h1><span class="etype">%s</span> %s</h1>'
               % (entity.dc_type().capitalize(), title))


class LinkOneLineView(baseviews.OneLineView):
    __select__ = is_instance('Link')

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        descr = entity.printable_value('description', format='text/plain')
        descr = descr and descr.splitlines()[0]
        values = {'title': xml_escape(entity.title),
                  'url': xml_escape(entity.absolute_url()),
                  'description': xml_escape(descr),
                  }
        self.w(u'<a href="%(url)s" title="%(description)s">%(title)s</a>'
               % values)
        self.w(u'&nbsp;[<a href="%s">%s</a>]'
               % (xml_escape(entity.url),
                  self._cw._('follow')))


class LinkView(EntityView):
    __regid__ = 'link'
    __select__ = is_instance('Link')
    title = _('link')

    def cell_call(self, row, col):
        entity = self.cw_rset.complete_entity(row, col)
        values = {'title': xml_escape(entity.title),
                  'url': xml_escape(entity.url),
                  'description': xml_escape(entity.printable_value('description')),
                  }
        self.w(u'<a href="%(url)s" title="%(description)s">%(title)s</a>'
               % values)

class XbelItemLinkView(xbel.XbelItemView):
    __select__ = is_instance('Link')

    def url(self, entity):
        return entity.url


class LinkFollowAction(action.Action):
    __select__ = one_line_rset() & is_instance('Link')
    __regid__ = 'follow'

    title = _('follow')
    category = 'mainactions'

    def url(self):
        return self.cw_rset.get_entity(self.cw_row or 0, self.cw_col or 0).url
