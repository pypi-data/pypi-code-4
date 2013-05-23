# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

from Products.Formulator import Widget, Validator
from Products.Formulator.DummyField import fields
from Products.Formulator.Field import ZMIField


def split_value(value):
    result = []
    for line in value:
        elements = line.split("|")
        if len(elements) >= 2:
            text, value = elements[:2]
        else:
            text = line
            value = line
        text = text.strip()
        value = value.strip()
        result.append((text, value))
    return result


class ListTextAreaWidget(Widget.TextAreaWidget):
    default = fields.ListTextAreaField('default',
                                       title='Default',
                                       default=[],
                                       required=0)

    def render(self, field, key, value, REQUEST):
        if value is None:
            value = field.get_value('default')
        if isinstance(value, basestring):
            # This happens while redisplaying a value from the request
            # i.e. _get_default(field, None, request)
            value = split_value(value.splitlines())
        lines = []
        for element_text, element_value in value:
            lines.append("%s | %s" % (element_text, element_value))
        lines = '\n'.join(lines)
        return Widget.TextAreaWidget.render(self, field, key, lines, REQUEST)

ListTextAreaWidgetInstance = ListTextAreaWidget()


class ListLinesValidator(Validator.LinesValidator):
    """A validator that can deal with lines that have a | separator
    in them to split between text and value of list items.
    """

    def validate(self, field, key, REQUEST):
        value = Validator.LinesValidator.validate(self, field, key, REQUEST)
        return split_value(value)

ListLinesValidatorInstance = ListLinesValidator()


class ListTextAreaField(ZMIField):
    meta_type = "ListTextAreaField"

    # field only has internal use
    internal_field = 1

    widget = ListTextAreaWidgetInstance
    validator = ListLinesValidatorInstance




