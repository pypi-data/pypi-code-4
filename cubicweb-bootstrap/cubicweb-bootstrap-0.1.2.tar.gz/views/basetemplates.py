# -*- coding: utf-8 -*-
"""bootstrap implementation of base templates

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch
from logilab.mtconverter import xml_escape

from cubicweb.predicates import anonymous_user, match_kwargs
from cubicweb.web import formwidgets as fw
from cubicweb.web.views import basetemplates# import LogForm, LogFormView

_ = unicode

basetemplates.LogForm.needs_css = ()
basetemplates.LogForm.form_buttons = [
    fw.ResetButton(label=_('cancel'),
                   attrs={'class': 'btn',
                          'data-dismiss': 'modal'}),
    fw.SubmitButton(label=_('log in'),
                    attrs={'class': 'btn btn-primary'})]

@monkeypatch(basetemplates.LogFormView)
def call(self, id, klass, title=True, showmessage=True):
    w = self.w
    w(u'<div id="%s" class="modal %s">' % (id, klass))
    if title:
        stitle = self._cw.property_value('ui.site-title')
        if stitle:
            stitle = xml_escape(stitle)
        else:
            stitle = u'&#160;'
        w(u'<div class="modal-header">'
          u'<h2>%s</h2>'
          u'</div>' % stitle)
    w(u'<div class="modal-body">')
    if showmessage and self._cw.message:
        w(u'<div class="alert alert-error">%s'
          u'<button class="close" data-dismiss="alert">x</button></div>' % self._cw.message)
    config = self._cw.vreg.config
    if config['auth-mode'] != 'http':
        self.login_form(id) # Cookie authentication
    w(u'</div>')
    if self._cw.https and config.anonymous_user()[0]:
        path = xml_escape(config['base-url'] + self._cw.relative_path())
        w(u'<div class="loginMessage alert"><a href="%s">%s</a></div>\n'
          % (path, self._cw._('No account? Try public access at %s') % path))
    w(u'</div>')
