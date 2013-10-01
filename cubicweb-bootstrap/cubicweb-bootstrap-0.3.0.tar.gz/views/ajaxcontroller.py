# -*- coding: utf-8 -*-
"""bootstrap implementation of ajax controllers

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb.utils import UStringIO
from cubicweb.web.views import ajaxcontroller


@monkeypatch(ajaxcontroller.AjaxFunction)
def _call_view(self, view, paginate=False, **kwargs):
    divid = self._cw.form.get('divid')
    # we need to call pagination before with the stream set
    try:
        stream = view.set_stream()
    except AttributeError:
        stream = UStringIO()
        kwargs['w'] = stream.write
        assert not paginate
    if divid == 'pageContent':
        # ensure divid isn't reused by the view (e.g. table view)
        del self._cw.form['divid']
        # mimick main template behaviour
        stream.write(u'<div class="col-md-12" id="pageContent">')
        vtitle = self._cw.form.get('vtitle')
        if vtitle:
            stream.write(u'<h1 class="vtitle">%s</h1>\n' % vtitle)
        paginate = True
    nav_html = UStringIO()
    if paginate and not view.handle_pagination:
        view.paginate(w=nav_html.write)
    stream.write(nav_html.getvalue())
    if divid == 'pageContent':
        stream.write(u'<div id="contentmain">')
    view.render(**kwargs)
    extresources = self._cw.html_headers.getvalue(skiphead=True)
    if extresources:
        stream.write(u'<div class="ajaxHtmlHead">\n') # XXX use a widget ?
        stream.write(extresources)
        stream.write(u'</div>\n')
    if divid == 'pageContent':
        stream.write(u'</div>%s</div>' % nav_html.getvalue())
    return stream.getvalue()
