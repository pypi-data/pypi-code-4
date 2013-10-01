"""bootstrap implementation of htmlwidgets

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from cubicweb.web import htmlwidgets

class MainToolbarBoxMenu(htmlwidgets.BoxMenu):

    def _start_li(self):
        return u'<li class="dropdown">'

    def _begin_menu(self):
        self.w(u'<ul class="dropdown-menu">')

    def _render(self):
        if self.isitem:
            self.w(self._start_li())
        ident = self.ident
        self.w(u'<a href="#" class="dropdown-toggle" data-toggle="dropdown">%s' % (
            self.label))
        self.w(u'<span class="caret"></span></a>')
        self._begin_menu()
        for item in self.items:
            bwcompatible_render_item(self.w, item)
        self._end_menu()
        if self.isitem:
            self.w(u'</li>')

class Separator(object):
    """a menu separator.

    Use this rather than `cw.web.htmlwidgets.BoxSeparator`.
    """
    newstyle = True

    def render(self, w):
        w(u'<li class="divider"></li>')


def bwcompatible_render_item(w, item):
    if hasattr(item, 'render'):
        if getattr(item, 'newstyle', False):
            if isinstance(item, Separator):
                item.render(w)
            else:
                w(u'<li>')
                item.render(w)
                w(u'</li>')
        else:
            item.render(w) # XXX displays <li> by itself
    else:
        w(u'<li>%s</li>' % item)

@monkeypatch(htmlwidgets.PopupBoxMenu)
def _render(self):
    self.w(u'<div id="%s" class="btn-group">' % self.ident)
    self.w(u'<a class="btn btn-default btn-sm dropdown-toggle" data-toggle="dropdown" href="#">'
           u' %s '
           u'<span class="caret"></span>'
           u'</a>' % self.label)
    self.w(u'<ul class="dropdown-menu pull-right">')
    for item in self.items:
        bwcompatible_render_item(self.w, item)
    self.w(u'</ul>')
    self.w(u'</div>')

