from __future__ import absolute_import, unicode_literals
from django.conf import settings
from gollum.fields import BoundField
from gollum.utils import FieldValues


class FormMarkupMixin(object):
    """Mixin class that adds intelligent addition of HTML and
    CSS attributes to form widgets.
    """
    def __init__(self, *args, **kwargs):
        super(FormMarkupMixin, self).__init__(*args, **kwargs)

        # Get this class' method resolution order and reverse it;
        # this way, I can apply HTML and CSS anywhere that it's declared
        # in the class' ancestry tree.
        rev_mro = type(self).mro()
        rev_mro.reverse()

        # Put together a dictionary of HTML attributes.
        html_attrs = FieldValues()
        for class_ in rev_mro:
            # If this class doesn't define an Attrs inner class,
            # skip it.
            if not hasattr(class_, 'Attrs'):
                continue

            # Iterate over the values provided.
            html_attrs.update(self.fields, class_.Attrs)

        # Put together a dictionary of CSS classes.
        css_classes = FieldValues()
        for class_ in rev_mro:
            # If the class doesn't define a CSS inner class,
            # skip it.
            if not hasattr(class_, 'CSS'):
                continue

            # Iterate over the values provided.
            css_classes.update(self.fields, class_.CSS)

        # Save the HTML attrs to the widgets of each of the fields.
        for field_name, attrs in html_attrs.items():
            self.fields[field_name].widget.attrs.update(attrs)

        # Save the extra CSS classes to the widget as a new property,
        # so it can be rendered using our BoundField subclass.
        for field_name, css in css_classes.items():
            self.fields[field_name].widget.css_classes = css

    def __getitem__(self, key):
        """Return a BoundField associated with the given field."""

        # Get the field.
        try:
            field = self.fields[key]
        except KeyError:
            raise KeyError('Field "%s" does not exist.' % key)

        # Return the BoundField.
        return BoundField(self, field, key)
