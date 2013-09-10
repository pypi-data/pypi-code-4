##############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""Checkbox widget with div tag separation
$Id: checkbox.py 3840 2013-09-10 12:55:33Z adam.groszer $
"""
__docformat__ = 'restructuredtext'

import zope.interface
import zope.i18n
import zope.schema.interfaces
import zope.schema.vocabulary

import z3c.form.term
import z3c.form.widget
import z3c.form.browser.checkbox
import z3c.form.browser.widget

from p01.form import interfaces
from p01.form.widget.widget import setUpWidget


# XXX: backport this to z3c.form
class CheckBoxWidget(z3c.form.browser.widget.HTMLInputWidget,
    z3c.form.widget.SequenceWidget):
    """Input type checkbox widget implementation using div instead of span tag.
    """

    zope.interface.implementsOnly(interfaces.ICheckBoxWidget)

    hint = None

    klass = u'checkbox'
    css = u'checkbox'

    @property
    def css(self):
        """Returns a CSS layout wrapper class name"""
        if self.hint is not None:
            # use hint as css class if hint is given
            return u'hint'
        else:
            # use text as css class
            return 'checkbox'

# XXX: backport this to z3c.form
    def isChecked(self, term):
        return term.token in self.value

# XXX: backport this to z3c.form
    def items(self):
        items = []
        append = items.append
        for count, term in enumerate(self.terms):
            checked = self.isChecked(term)
            id = '%s-%i' % (self.id, count)
            if zope.schema.interfaces.ITitledTokenizedTerm.providedBy(term):
                label = zope.i18n.translate(term.title, context=self.request,
                                  default=term.title)
            else:
                label = unicode(term.value)
            append(
                {'id':id, 'name':self.name + ':list', 'value':term.token,
                 'label':label, 'checked':checked})
        return items


class DivCheckBoxWidget(CheckBoxWidget):
    """CheckBoxWidget using a div wrapper for option tags"""


#class SingleCheckBoxWidget(z3c.form.browser.checkbox.SingleCheckBoxWidget):
class SingleCheckBoxWidget(CheckBoxWidget):
    """Input type checkbox widget implementation using div instead of span tag.
    """

    zope.interface.implementsOnly(interfaces.ISingleCheckBoxWidget)

    klass = u'checkbox'
    css = u'checkbox'

    klass = u'single-checkbox-widget'

    def updateTerms(self):
        if self.terms is None:
            self.terms = z3c.form.term.Terms()
            self.terms.terms = zope.schema.vocabulary.SimpleVocabulary((
                zope.schema.vocabulary.SimpleTerm('selected', 'selected',
                                      self.label or self.field.title), ))
        return self.terms


class SingleDivCheckBoxWidget(SingleCheckBoxWidget):
    """SingleCheckBoxWidget using a div wrapper for option tags"""


class SingleCheckBoxWithoutLabelWidget(SingleCheckBoxWidget):
    """SingleCheckBoxWidget widget without label.

    This widget is usabel in a table cell where you provide a table header
    and don't like to repeat the checkbox label in each cell
    """

    klass = u'single-checkbox-without-label'


# get
def getCheckBoxWidget(field, request):
    """IFieldWidget factory for CheckBoxWidget."""
    return z3c.form.widget.FieldWidget(field, CheckBoxWidget(request))


def getDivCheckBoxWidget(field, request):
    """IFieldWidget factory for DivCheckBoxWidget."""
    return z3c.form.widget.FieldWidget(field, DivCheckBoxWidget(request))


def getSingleCheckBoxWidget(field, request):
    """IFieldWidget factory for SingleCheckBoxWidget."""
    return z3c.form.widget.FieldWidget(field, SingleCheckBoxWidget(request))


def getSingleDivCheckBoxWidget(field, request):
    """IFieldWidget factory for SingleDivCheckBoxWidget."""
    return z3c.form.widget.FieldWidget(field, SingleDivCheckBoxWidget(request))


def getSingleCheckBoxWithoutLabelWidget(field, request):
    """IFieldWidget factory for SingleDivCheckBoxWidget."""
    widget = z3c.form.widget.FieldWidget(field,
        SingleCheckBoxWithoutLabelWidget(request))
    widget.label = u'' # don't show the label (twice)
    return widget


# setup
def setUpCheckBoxWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(CheckBoxWidget, **kw)


def setUpDivCheckBoxWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(DivCheckBoxWidget, **kw)


def setUpSingleCheckBoxWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(SingleCheckBoxWidget, **kw)


def setUpSingleDivCheckBoxWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(SingleDivCheckBoxWidget, **kw)


def setUpSingleCheckBoxWithoutLabelWidget(**kw):
    """Widget creator method supporting kw arguments"""
    return setUpWidget(SingleCheckBoxWithoutLabelWidget, **kw)
