"""
Implementation of json-patch draft 04:

http://tools.ietf.org/html/draft-pbryan-json-patch-04
"""

from json_pointer import Pointer, PointerError


class PatchError(Exception):
    """
    Error raised when a patch fails
    """
    pass


class Patch(list):
    """
    Representation of a json-patch

    >>> from json_patch import Patch
    >>> patch = Patch([
        {
            'op': 'add'
            'path': '/c',
            'value': 'f'
        },
        {
            'op': 'remove':
            'path': '/a'
        },
        {
            'op': 'replace'
            'path': '/b',
            'value': 'g'
        }
    ])
     >>> data = {'a': 'd', 'b': 'e'}
     >>> print patch.apply(data)
      {'b': 'g', 'c': 'f'}

    """
    def apply(self, data):
        """
        Apply the patch to `data`

        :params data: data to patch
        :returns: patched data
        :raises Pointer: when the patch fails
        """
        for operation in self:
            data = self._operate(data, operation)

        return data

    def _operate(self, data, operation):
        """
        Perform a single operation on `data`
        """
        try:
            func = getattr(self, '_%s' % operation['op'])
        except KeyError:
            raise PatchError('Missing "op" in patch"')
        except AttributeError:
            raise PatchError('Invalid operation: %s' % operation['op'])
        
        try:
            pointer = Pointer(operation['path'])
            data = func(data, pointer, operation)
        except PointerError, e:
            raise PatchError('Could not apply patch: %s' % e)
        
        return data

    def _add(self, data, pointer, operation):
        """
        Perform an add operation on `data`

        """
        if not pointer._references:
            return operation['value']

        pointer.set(data, operation['value'])
        
        return data

    def _remove(self, data, pointer, operation):
        """
        Perform a remove operation on data
        """
        pointer.unset(data)
        return data

    def _replace(self, data, pointer, operation):
        """
        Perform a replace operation on `data`
        """
        self._remove(data, pointer, operation)
        self._add(data, pointer, operation)

        return data

    def _move(self, data, pointer, operation):
        """
        Perform a move operation on `data`
        """
        from_ = Pointer(operation['from'])
        value = from_.get(data)
        from_.unset(data)
        pointer.set(data, value)
        
        return data

    def _copy(self, data, pointer, operation):
        """
        Perform a copy operation on `data`
        """
        from_ = Pointer(operation['from'])
        
        value = from_.get(data)
        pointer.set(data, value)
        
        return data

    def _test(self, data, pointer, operation):
        """
        Perform a test operation on `data`
        """
        try:
            pointer.get(data)
        except PointerError:
            raise PatchError(
                'Test failed: %s not set' % (pointer, )
            )

        if not pointer.get(data) == operation['value']:
            raise PatchError(
                'Test failed: %s != %s' % (pointer.get(data), operation['value'])
            )

        return data
