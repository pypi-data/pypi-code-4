"""bootstrap implementation of formwidgets

:organization: Logilab
:copyright: 2013 LOGILAB S.A. (Paris, FRANCE), license is LGPL.
:contact: http://www.logilab.fr/ -- mailto:contact@logilab.fr
"""

__docformat__ = "restructuredtext en"

from logilab.common.decorators import monkeypatch

from cubicweb.web import formwidgets

formwidgets.ButtonInput.css_class = 'btn btn-default'
formwidgets.Button.css_class = 'btn btn-default'
formwidgets.SubmitButton.css_class = 'btn btn-primary'

@monkeypatch(formwidgets.FieldWidget)
def attributes(self, form, field):
    """Return HTML attributes for the widget, automatically setting DOM
    identifier and tabindex when desired (see :attr:`setdomid` and
    :attr:`settabindex` attributes)
    """
    attrs = dict(self.attrs)
    if self.setdomid:
        attrs['id'] = field.dom_id(form, self.suffix)
    if self.settabindex and not 'tabindex' in attrs:
        attrs['tabindex'] = form._cw.next_tabindex()
    attrs['class'] = 'form-control'
    return attrs
