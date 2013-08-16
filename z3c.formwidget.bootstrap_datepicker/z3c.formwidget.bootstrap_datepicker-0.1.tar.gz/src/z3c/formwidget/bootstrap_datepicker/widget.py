# -*- coding: utf-8 -*-
"""A twitter bootstrap datepicker widget for z3c.form."""

# python imports
import string

# zope imports
from z3c.form import interfaces
from z3c.form.browser import widget
from z3c.form.browser.text import TextWidget
from z3c.form.widget import FieldWidget
from zope.component import adapter
from zope.schema.interfaces import (IFromUnicode, ITextLine)
from zope.interface import implementer, implements

# local imports
from z3c.formwidget.bootstrap_datepicker.fanstaticlibs import (
  bootstrapdatepicker,
  bootstrapdatepicker_locales,
)
from z3c.formwidget.bootstrap_datepicker.interfaces import (
  IBootstrapDatepickerWidget,
)


class BootstrapDatepickerWidget(TextWidget):
    """Date Picker widget."""
    implements(IBootstrapDatepickerWidget, IFromUnicode)

    klass = u'bootstrap-datepicker-widget'

    format = u'm/d/yy'
    language = u'en'
    startView = u'month'

    _javascript_input = """
jQuery("#${id}-component").datepicker({
  autoclose: true,
  format: '${format}',
  language: '${language}',
  startView: '${startView}',
  todayBtn: true,
  todayHighlight: true
});"""

    def update(self):
        """See z3c.form.interfaces.IWidget."""
        bootstrapdatepicker.need()
        super(BootstrapDatepickerWidget, self).update()
        widget.addFieldClass(self)

    def javascript_input(self):
        if self.language in bootstrapdatepicker_locales:
            bootstrapdatepicker_locales[self.language].need()
        return string.Template(self._javascript_input).substitute(dict(
            format=self.format,
            id=self.id,
            language=self.language,
            startView=self.startView,
        ))


@adapter(ITextLine, interfaces.IFormLayer)
@implementer(interfaces.IFieldWidget)
def BootstrapDatepickerFieldWidget(field, request):
    """Factory for BootstrapDatepickerWidget."""
    return FieldWidget(field, BootstrapDatepickerWidget(request))
