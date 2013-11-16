from django.forms import widgets


class NumberTextInput(widgets.TextInput):
    """
    A TextInput subclass that omits all non-digit characters when rendering.
    """
    def render(self, name, value, attrs=None):
        trimmed = ''
        for char in unicode(value):
            if char.isdigit():
                trimmed += char
        return super(NumberTextInput, self).render(name, trimmed, attrs)


class HiddenIntegerInput(widgets.HiddenInput):
    """
    A HiddenInput that ensures that the value is an integer.
    """
    def render(self, name, value, attrs=None):
        return super(HiddenIntegerInput, self).render(name, int(value), attrs)
