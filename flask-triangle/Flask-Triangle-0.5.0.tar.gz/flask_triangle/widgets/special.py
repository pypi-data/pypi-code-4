# -*- encoding: utf-8 -*-
"""
    template
    --------

    :copyright: (c) 2013 by Morgan Delahaye-Prat.
    :license: BSD, see LICENSE for more details.
"""


from __future__ import absolute_import
from __future__ import unicode_literals

from .base import Widget


class Label(Widget):
    """
    Render a text instead of an ``<input>`` field.

    This widget is useful if you want to provide the same form but with no
    input on some fields.
    """

    html_template = '<span {attributes}>{{{{{{{{{bind}}}}}}}}}</span>'
    json_type = None

    def __init__(self, bind, name=None, validators=None, label=None,
                 description=None, html_attributes=None):

        super(Label, self).__init__(bind, name, validators, label, description,
                                    html_attributes)

        self._bind = bind
        del self.attributes['ng-model']

    def render(self):
        return self.html_template.format(attributes=unicode(self.attributes),
                                         bind=self._bind)

    @property
    def schema(self):
        return dict()
