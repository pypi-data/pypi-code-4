import pkg_resources

from plone.formwidget.datetime import MessageFactory as _
from z3c.form.interfaces import IWidget
from zope.schema import ValidationError

try:
    pkg_resources.get_distribution('plone.schemaeditor')
    from plone.schemaeditor.schema import IDate, IDatetime
except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict), e:
    # No dexterity
    from zope.schema.interfaces import IDate, IDatetime


# Fields

class IDateField(IDate):
    """Special marker for date fields that use our widget.
    """


class IDatetimeField(IDatetime):
    """Special marker for datetime fields that use our widget.
    """


# Widgets

class IDateWidget(IWidget):
    """Date widget marker for z3c.form.
    """


class IDatetimeWidget(IWidget):
    """Datetime widget marker for z3c.form.
    """


class IMonthYearWidget(IWidget):
    """MonthYear widget marker for z3c.form.
    """


class IYearWidget(IWidget):
    """Year widget marker for z3c.form.
    """


# Errors

class DateValidationError(ValidationError):
    __doc__ = _(u'Please enter a valid date.')


class DatetimeValidationError(ValidationError):
    __doc__ = _(u'Please enter a valid date and time.')
