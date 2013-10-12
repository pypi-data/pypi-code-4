# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Branko Majic
#
# This file is part of Django Conntrackt.
#
# Django Conntrackt is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Django Conntrackt is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Django Conntrackt.  If not, see <http://www.gnu.org/licenses/>.
#


# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Branko Majic
#
# This file is part of Django Conntrackt.
#
# Django Conntrackt is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Django Conntrackt is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# Django Conntrackt.  If not, see <http://www.gnu.org/licenses/>.
#


# Django imports.
from django.forms import ModelForm

# Application imports.
from .models import Project, Location, Entity, Interface, Communication


class WidgetCSSClassFormMixin(object):
    """
    Helper form mixin that can be used for applying additional custom CSS
    classes to form field widgets.

    The mixin accepts the following class options:

        widget_css_classes - Dictionary describing which additional CSS classes
        should be applied to which form widget. Dictinoary keys should be equal
        to form widget names, while the value should be a string containing the
        extra CSS classes that should be applied to it. In order to apply the
        CSS classes to every widget of the form, use the key "ALL"
    """

    def __init__(self, *args, **kwargs):
        """
        Assigns the custom CSS classes form widgets, as configured by the
        widget_css_classes property.
        """

        super(WidgetCSSClassFormMixin, self).__init__(*args, **kwargs)

        for field_name, css_class in self.widget_css_classes.iteritems():
            if field_name == "ALL":
                for field in self.fields.values():
                    if "class" in field.widget.attrs:
                        field.widget.attrs["class"] += " " + css_class
                    else:
                        field.widget.attrs["class"] = css_class
            else:
                field = self.fields[field_name]
                if "class" in field.widget.attrs:
                    field.widget.attrs["class"] += " " + css_class
                else:
                    field.widget.attrs["class"] = css_class


class PlaceholderFormMixin(object):
    """
    Helper form mixin that can be used to set-up placeholders for text widgets.

    The mixin accepts the following class options:

        widget_placeholders - Dictionary describing which placeholders should be
        applied to which widgets. Keys should be equal to form widget names,
        while the values should be the strings that should be set as
        placeholders.
    """

    def __init__(self, *args, **kwargs):
        """
        Assigns the placeholders to text form widgets, as configured by the
        widget_placeholders property.
        """

        super(PlaceholderFormMixin, self).__init__(*args, **kwargs)

        for field_name, placeholder in self.widget_placeholders.iteritems():
            self.fields[field_name].widget.attrs["placeholder"] = placeholder


class EntityForm(WidgetCSSClassFormMixin, PlaceholderFormMixin, ModelForm):
    """
    Implements a custom model form for entities with some styling changes.
    """

    class Meta:
        model = Entity

    widget_placeholders = {"name": "Entity name",
                           "description": "Entity description"}
    widget_css_classes = {"ALL": "span6"}


class InterfaceForm(WidgetCSSClassFormMixin, PlaceholderFormMixin, ModelForm):
    """
    Implements a custom model form for interfaces with some styling changes.
    """

    class Meta:
        model = Interface

    widget_placeholders = {"name": "Interface name",
                           "description": "Interface description",
                           "address": "IP address of interface",
                           "netmask": "IP address netmask"}

    widget_css_classes = {"ALL": "span6"}


class CommunicationForm(WidgetCSSClassFormMixin, PlaceholderFormMixin, ModelForm):
    """
    Implements a custom model form for communications with some styling changes.
    """

    class Meta:
        model = Communication

    widget_placeholders = {"port": "Port used for communication",
                           "description": "Communication description"}

    widget_css_classes = {"ALL": "span6"}


class ProjectForm(WidgetCSSClassFormMixin, PlaceholderFormMixin, ModelForm):
    """
    Implements a custom model form for projects with some styling changes.
    """

    class Meta:
        model = Project

    widget_placeholders = {"name": "Project name",
                           "description": "Project description"}

    widget_css_classes = {"ALL": "span6"}


class LocationForm(WidgetCSSClassFormMixin, PlaceholderFormMixin, ModelForm):
    """
    Implements a custom model form for projects with some styling changes.
    """

    class Meta:
        model = Location

    widget_placeholders = {"name": "Location name",
                           "description": "Location description"}

    widget_css_classes = {"ALL": "span6"}
