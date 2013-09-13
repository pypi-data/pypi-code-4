from __future__ import absolute_import, unicode_literals
from sdict import adict


class FieldValues(dict):
    """A dict subclass that accepts a dictionary of fields and an inner
    form Attrs or CSS class.
    """
    def __init__(self):
        super(FieldValues, self).__init__()

    def update(self, fields, payload_class):
        """Write the values from the `payload_class` (an Attrs or CSS
        inner class) to this dictionary.
        """
        for key in dir(payload_class):
            # Ignore dunder members.
            if key.startswith('__') and key.endswith('__'):
                continue

            # Sanity check: Does this key actually exist in the
            # list of fields? If it doesn't, we have an error.
            if key not in fields:
                raise AttributeError(' '.join((
                    'Unable to assign display properties to field',
                    '"%s", because it does not exist.' % key,
                )))

            # Convert our value to the appropriate type.
            value = getattr(payload_class, key)
            if payload_class.__name__ == 'CSS':
                if hasattr(value, 'split'):
                    value = value.split()
                value = set(value)
            elif payload_class.__name__ == 'Attrs':
                value = adict(value)
            else:
                raise TypeError('Unrecognized payload class.')

            # Save the value. If the value already exists, update
            # appropriately.
            if key in self:
                if isinstance(self[key], set):
                    self[key] = self[key].union(value)
                else:
                    self[key].update(value)
            else:
                self[key] = value
