# -*- coding: utf-8 -*-
"""bootstrap implementation of base components

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb.web.views import basecomponents
from cubicweb.uilib import js


# handle automatic reload
orig_render_impl = getattr(basecomponents.ApplLogo, '_original_render_impl_', None)
if orig_render_impl is None:
    # first time we land here
    orig_render_impl = basecomponents.ApplLogo.render
    basecomponents.ApplLogo._original_render_impl_ = orig_render_impl

@monkeypatch(basecomponents.ApplLogo)
def render(self, w):
    w(u'<h1>')
    self._original_render_impl_(w)
    w(u'</h1>')

basecomponents.CookieLoginComponent._html = (
    u'''<!--%s-->
    <a title="%s" class="btn btn-default btn-info" data-toggle="modal"
    href="#loginModal">%s</a>''')

@monkeypatch(basecomponents.CookieLoginComponent)
def call(self):
    self.w(self._html % (self._cw._('login / password'),
                         self.loginboxid, self._cw._('i18n_login_popup')))
    self._cw.add_onload(js.jQuery("body").append(
        self._cw.view('logform', rset=self.cw_rset, id=self.loginboxid,
                      klass='%s' % self.loginboxid, title=True,
                      showmessage=False)))


# NOTE: CW 3.18 may introduce render_messages(). This would be the
#       the only method to override
@monkeypatch(basecomponents.ApplicationMessage)
def call(self, msg=None):
    if msg is None:
        msgs = []
        if self._cw.cnx:
            srcmsg = self._cw.get_shared_data('sources_error', pop=True)
            if srcmsg:
                msgs.append(srcmsg)
        reqmsg = self._cw.message # XXX don't call self._cw.message twice
        if reqmsg:
            msgs.append(reqmsg)
    else:
        msgs = [msg]
    ########## <cwpatch> ##########
    for msg in msgs:
        # XXX should we prefer alert-info to alert- -success as default value
        self.w(u'<div class="alert alert-success" id="%s">'
               u'<button class="close" data-dismiss="alert" type="button">x</button>'
               u' %s</div>' % (self.domid, msg))
    ########## </cwpatch> ##########


@monkeypatch(basecomponents.ApplicationName)
def render(self, w, **kwargs):
    title = self._cw.property_value('ui.site-title')
    if title:
        w(u'<a class="navbar-brand" href="%s">%s</a>'
          % (self._cw.base_url(), xml_escape(title)))
