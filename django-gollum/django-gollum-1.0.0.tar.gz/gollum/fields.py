from __future__ import absolute_import, unicode_literals
from django.conf import settings
from django.forms.forms import BoundField as DjangoBoundField
import six


class BoundField(DjangoBoundField):
    """BoundField subclass that is aware of extra CSS classes
    on the field.
    """
    def as_widget(self, widget=None, attrs=None, css_classes=None,
                        only_initial=False):
        """Return a string representing the HTML rendering of this
        field.
        """
        # Get the CSS classes provided to this method into a standard
        # format (a Python set).
        if not css_classes:
            css_classes = []
        if isinstance(css_classes, six.binary_type):
            css_classes = css_classes.decode('utf8')
        if hasattr(css_classes, 'split'):
            css_classes = css_classes.split()
        css_classes = set(css_classes)

        # Add any CSS classes that should innately exist on this field
        # to the field.
        css_classes = css_classes.union(self.css_classes().split(' '))

        # If any classes are specified on `attrs` directly, add them
        # to the set so they aren't blown away.
        if not attrs:
            attrs = {}
        css_classes = css_classes.union(attrs.get('class', '').split(' '))

        # Add the CSS classes to the HTML attributes dict.
        attrs['class'] = ' '.join(css_classes)

        # Add any attributes we are given.
        if hasattr(settings, 'FORM_GLOBAL_ATTRS'):
            attrs.update(settings.FORM_GLOBAL_ATTRS)
        if self.field.required and hasattr(settings, 'FORM_REQUIRED_ATTRS'):
            attrs.update(settings.FORM_REQUIRED_ATTRS)
        if (not self.field.required and
                        hasattr(settings, 'FORM_OPTIONAL_ATTRS')):
            attrs.update(settings.FORM_OPTIONAL_ATTRS)

        # Now return the superclass implementation.
        return super(BoundField, self).as_widget(widget=widget, attrs=attrs,
                                                 only_initial=only_initial)

    def css_classes(self, extra_classes=None):
        """Returns a string of space-separated CSS classes
        for this field.
        """
        # Run the superclass method, but split the result back
        # on space, as we may want to add more.
        answer = super(BoundField, self).css_classes(
            extra_classes=extra_classes
        ).split(' ')
        answer = set(answer)

        # If any CSS classes are defined on the field's widget, add
        # them as well.
        if hasattr(self.field.widget, 'css_classes'):
            answer = answer.union(self.field.widget.css_classes)

        # If this field is required or in error, and classes for this
        # are defined in settings, add those.
        if (self.field.required and
                    hasattr(settings, 'FORM_REQUIRED_CSS_CLASS')):
            answer.add(settings.FORM_REQUIRED_CSS_CLASS)
        if self.errors and hasattr(settings, 'FORM_ERROR_CSS_CLASS'):
            answer.add(settings.FORM_ERROR_CSS_CLASS)

        # Return the final answer.
        return ' '.join(answer)
