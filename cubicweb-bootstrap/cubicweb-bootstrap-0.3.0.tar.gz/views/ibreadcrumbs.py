"""bootstrap implementation of boxes

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from cubicweb.entity import Entity
from cubicweb.web.views import ibreadcrumbs

@monkeypatch(ibreadcrumbs.BreadCrumbEntityVComponent)
def render(self, w, **kwargs):
    #XXX we do not need first sepator for this breadcrumb style
    self.first_separator = False
    try:
        entity = self.cw_extra_kwargs['entity']
    except KeyError:
        entity = self.cw_rset.get_entity(0, 0)
    adapter = ibreadcrumbs.ibreadcrumb_adapter(entity)
    view = self.cw_extra_kwargs.get('view')
    path = adapter.breadcrumbs(view)
    if path:
        w(u'<ul class="breadcrumb">')
        if self.first_separator:
            w(u'<li><span class="divider">%s</span></li>' % self.separator)
        self.render_breadcrumbs(w, entity, path)
        w(u'</ul>')


@monkeypatch(ibreadcrumbs.BreadCrumbEntityVComponent)
def render_breadcrumbs(self, w, contextentity, path):
    root = path.pop(0)
    if isinstance(root, Entity):
        w(u'<li>%s<span class="divider">%s</span></li>' %
          (self.link_template % (self._cw.build_url(root.__regid__),
                                 root.dc_type('plural')), self.separator))
    liclass = u' class="active"' if not path else u''
    w(u'<li%s>' % liclass)
    self.wpath_part(w, root, contextentity, not path)
    w(u'</li>')
    for i, parent in enumerate(path):
        last = i == len(path) - 1
        liclass = u' class="active"' if last else u''
        w(u'<li%s><span class="divider">%s</span>' % (liclass, self.separator))
        self.wpath_part(w, parent, contextentity, last)
        w(u'</li>')
