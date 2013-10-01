# -*- coding: utf-8 -*-
"""bootstrap implementation of boxes

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from functools import partial

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb.utils import wrap_on_write
from cubicweb.web.views import boxes

from cubes.bootstrap.views.htmlwidgets import (MainToolbarBoxMenu,
                                               bwcompatible_render_item)

boxes.SearchBox.formdef = (
    u'<div id="search-box">'
    u'<form action="%(action)s">'
    u'<input id="norql" type="text" accesskey="q" tabindex="%(tabindex1)s"'
    u'       title="search text" value="%(value)s" name="rql"'
    u'       class="search-query" placeholder="%(searchlabel)s"/>'
    u'       <input type="hidden" name="__fromsearchbox" '
    u'              value="1" />'
    u'       <input type="hidden" name="subvid" '
    u'value="tsearch" />'
    #FIXME this commented html code is left because the string
    #replacement would fail unless the render method is modified
    #also
    u'<!--input tabindex="%(tabindex2)s" type="submit" id="rqlboxsubmit"'
    u'    class="rqlsubmit" value="" /-->'
    u'</form></div>')

@monkeypatch(boxes.SearchBox)
def render_body(self, w):
    # Don't display search box title, just display the search box body
    if self._cw.form.pop('__fromsearchbox', None):
        rql = self._cw.form.get('rql', '')
    else:
        rql = ''
    w(self.formdef % {'action': self._cw.build_url('view'),
                      'tabindex1': self._cw.next_tabindex(),
                      'value': xml_escape(rql),
                      'tabindex2': self._cw.next_tabindex(),
                      'searchlabel': self._cw._('Search')})


@monkeypatch(boxes.EditBox)
def _get_menu(self, id, title=None, label_prefix=None):
    try:
        return self._menus_by_id[id]
    except KeyError:
        if title is None:
            title = self._cw._(id)
        ## <cwpatch> use MainToolbarBoxMenu instead of BoxMenu
        self._menus_by_id[id] = menu = MainToolbarBoxMenu(title)
        ## </cwpatch>
        menu.label_prefix = label_prefix
        self._menus_in_order.append(menu)
        return menu

@monkeypatch(boxes.EditBox)
def render_body(self, w):
    self.render_items(w, klass='unstlyed')


def contextualbox_render(self, w):
    if self.init_rendering():
        view = self.cw_extra_kwargs['view']
        w(u'<div class="panel panel-default %s %s" id="%s">' % (self.cssclass, view.cssclass,
                                            view.domid))
        with wrap_on_write(w, u'<h5 class="panel-heading panel-title">',
                           u'</h5>') as wow:
            view.render_title(wow)
        w(u'<div class="panel-body">')
        view.render_body(w)
        # We dissapear the boxFooter CSS place holder, as shadows
        # or effect will be made with CSS
        w(u'</div></div>\n')

# XXX partial
def contextualbox_render2(self, w):
    if self.init_rendering():
        view = self.cw_extra_kwargs['view']
        w(u'<div class="panel panel-default %s %s" id="%s">' % (self.cssclass, view.cssclass,
                                            view.domid))
        with wrap_on_write(w, u'<h5 class="panel-heading panel-title">',
                           u'</h5>') as wow:
            view.render_title(wow)
        w(u'<div class="panel-body">')
        view.render_body(w)
        # We dissapear the boxFooter CSS place holder, as shadows
        # or effect will be made with CSS
        w(u'</div></div>\n')

setattr(boxes.ContextualBoxLayout, 'render', contextualbox_render)
setattr(boxes.ContextFreeBoxLayout, 'render', contextualbox_render2)



