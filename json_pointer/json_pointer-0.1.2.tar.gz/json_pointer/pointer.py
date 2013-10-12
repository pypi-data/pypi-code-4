"""
Simple implementation of the json-pointer spec draft 01:

http://tools.ietf.org/html/draft-ietf-appsawg-json-pointer-01
"""


class PointerSyntaxError(Exception):
    pass


class PointerError(Exception):
    pass


class Pointer(object):
    """
    Json Pointer class. Represents a pointer to data in json

    >>> pointer = Pointer('/a/b')
    >>> data = {'a': {'b': 'c'}}
    >>> print pointer.get(data)
    c
    >>> pointer.unset(data)
    >>> print data
    {'a': {}}
    >>> pointer.set(data, 'd')
    >>> print pointer.get(data)
    d
    """
    def __init__(self, pointer):
        """
        Initialize the pointer

        :param pointer: A string representation of the json-pointer. Can also be al list
        """
        if isinstance(pointer, list):
            self._references = pointer
        elif pointer and not pointer.startswith('/'):
            raise PointerSyntaxError
        else:
            self._references = [reference.replace('~1', '/').replace('~0', '~') for
                                reference in pointer.split('/')[1:]]

    def _step(self, data, func, *args, **kwargs):
        try:
            if self._references[0] == '-':
                # '-': return None
                data = None
            elif isinstance(data, dict):
                # dict: return value
                data = data[self._references[0]]
            elif isinstance(data, list):
                # list: return member
                data = data[int(self._references[0])]
            else:
                # something else: Raise error
                raise PointerError()
        except (KeyError, IndexError, TypeError, ValueError), e:
            raise PointerError(e)

        # recurse
        return getattr(Pointer(self._references[1:]), func)(data, *args, **kwargs)
        
    def get(self, data):
        """
        Retrieve the value from data that the pointer points to

        >>> pointer = Pointer('/a/b')
        >>> data = {'a': {'b': 'c'}}
        >>> print pointer.get(data)
        c

        :param data: object from which the value is retrieved
        """
        if not self._references:
            # Recursion ended: return data
            return data
        else:
            return self._step(data, 'get')
        
    def unset(self, data):
        """
        Unset the value the pointer points to

        >>> pointer = Pointer('/a/b')
        >>> data = {'a': {'b': 'c'}}
        >>> pointer.unset(data)
        >>> print data
        {'a': {}}

        :param data: object from which the value is unset
        """
        if len(self._references) == 1:
            key = self._references[0]
            try:
                if key == '-':
                    raise PointerError()
                if isinstance(data, dict):
                    del data[key]
                elif isinstance(data, list):
                    del data[int(key)]
                else:
                    raise PointerError()
            except (IndexError, KeyError), e:
                raise PointerError(e)
        else:
            return self._step(data, 'unset')

    def set(self, data, value):
        """
        Set the value of the pointer

        >>> pointer = Pointer('/a/b')
        >>> data = {'a': {'b': 'c'}}
        >>> pointer.set(data, 'd')
        >>> print data
        {'a': {'b': 'd'}

        :param data: the object to set the value in
        :param value: the value to set it to
        """
        if len(self._references) == 1:
            key = self._references[0]
            try:
                if isinstance(data, list) and key == '-':
                    data.append(value)
                elif isinstance(data, dict):
                    data[key] = value
                elif isinstance(data, list) and int(key) >= 0 and int(key) <= len(data):
                    data.insert(int(key), value)
                else:
                    raise PointerError('Could not set value')
            except (IndexError, KeyError, ValueError), e:
                raise PointerError(e)
        else:
            return self._step(data, 'set', value)

    def __repr__(self):
        return '<Pointer: /%s>' % ('/'.join(self._references),)

    def __unicode__(self):
        return '/'.join(self._references)


