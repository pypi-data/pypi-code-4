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
                   attrs={'class': 'btn btn-default',
                          'data-dismiss': 'modal'}),
    fw.SubmitButton(label=_('log in'),
                    attrs={'class': 'btn btn-primary'})]

basetemplates.LogForm.form_renderer_id = 'modal-form-renderer'

@monkeypatch(basetemplates.LogFormView)
def call(self, id, klass, title=True, showmessage=True):
    w = self.w
    if not (showmessage or self._cw.message):
        showmessage = False
    stitle = '&#160;'
    if title:
        stitle = self._cw.property_value('ui.site-title')
        if stitle:
            stitle = xml_escape(stitle)
    config = self._cw.vreg.config
    if config['auth-mode'] != 'http':
        self.login_form(id, "loginModal", stitle, showmessage) # Cookie authentication
    if self._cw.https and config.anonymous_user()[0]:
        path = xml_escape(config['base-url'] + self._cw.relative_path())
        w(u'<div class="loginMessage alert"><a href="%s">%s</a></div>\n'
          % (path, self._cw._('No account? Try public access at %s') % path))

@monkeypatch(basetemplates.LogFormView)
def login_form(self, id, modal_id, title, showmessage):
    cw = self._cw
    form = cw.vreg['forms'].select('logform', cw)
    if cw.vreg.config['allow-email-login']:
        label = cw._('login or email')
    else:
        label = cw.pgettext('CWUser', 'login')
    form.field_by_name('__login').label = label
    form.render(w=self.w, table_class='', display_progress_div=False,
                modal_id=modal_id,
                title=title, showmessage=showmessage)
    cw.html_headers.add_onload('jQuery("#__login:visible").focus()')
