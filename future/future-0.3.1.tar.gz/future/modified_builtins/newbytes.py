"""
Backport of the bytes object from Python 3.

Yes, scary stuff. Why do this? Without it:
    ------------------------------------------------------------------
    Ran 203 tests in 0.214s
    
    FAILED (failures=31, errors=55, skipped=1)
    ------------------------------------------------------------------
when running

    $ python -m future.tests.test_bytes

which is backported from the test_bytes.py script from Py3.3.


"""

# from __future__ import unicode_literals

from future import standard_library, six
# from future.builtins import chr  - no, we want the 8-bit version

_oldbytes = bytes

if not six.PY3:
    class newbytes(_oldbytes):
        def __new__(cls, value):
            if isinstance(value[0], int):
                # It's a list of integers
                value = b''.join([chr(x) for x in value])
            return super(Bites, cls).__new__(cls, value)
            
        def itemint(self, index):
            return ord(self[index])
        
        def iterint(self):
            for x in self:
                yield ord(x)

class RawData(_oldbytes):
    '''
    This class stores bytes data in a similar way to the bytes object in Python
    3.x.
    '''
    def __init__(self, value=()):
        '''
        Takes an iterable value that should contain either integers in range(256)
        or corresponding characters.
        Some examples for working with RawData:

        >>> r = RawData('Hello world!')
        >>> r[0]
        RawData((0x48))
        >>> byte_tuple = (115, 101, 99, 114, 101, 116)
        >>> RawData(byte_tuple) == RawData('secret')
        True
        >>> RawData('Hello world!').toString()
        String('Hello world!')
        '''
        if isinstance(value, RawData):
            value = value._data
        else:
            if isinstance(value, int):
                value = (value,)
            if not (hasattr(value, '__iter__') or hasattr(value, '__getitem__')):
                raise TypeError('value must be iterable')
            if isinstance(value, _oldbytes):
                # this makes sure that iterating over value gives one byte at a time
                # in python 2 and 3
                if bytes == str:
                    # in python 2 iterating over bytes gives characters instead of integers
                    value = tuple(map(ord, value))
                else:
                    # Only tuple-ify if not already tuple-ified by map above
                    value = tuple(value)
            elif bytes==str and isinstance(value, unicode):
                value = tuple(map(ord, value.encode('utf-8')))
            elif isinstance(value, str):
                # only python3 strings here
                value = tuple(value.encode('utf-8'))
            elif isinstance(value, String):
                value = value.toRawData()._data
            else:
                # maybe a list of ints?
                try:
                    value = tuple(map(int, value))
                except ValueError:
                    raise ValueError('values must be ints')

                for i in value:
                    if i < 0 or i > 255:
                        raise ValueError('values not in range(256)')

        self._data = value

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self._data.__eq__(other._data)
        return NotImplemented

    def __add__(self, other):
        if not isinstance(other, self.__class__):        
            try:
                other = self.__class__(other)
            except (TypeError, ValueError):
                return NotImplemented
        return self.__class__(self._data.__add__(other._data))
    
    def __len__(self):
        return self._data.__len__()

    def __getitem__(self, key):
        return self.__class__(self._data.__getitem__(key))

    def __contains__(self, key):
        try:
            key = self.__class__(key)
        except (TypeError, ValueError):
            return False
        if len(key) > 1:
            return False
        return self._data.__contains__(key._data[0])

    def __iter__(self):
        return self._data.__iter__()

    def __hash__(self):
        return self._data.__hash__()

    def __repr__(self):
        return 'RawData((' + ','.join(map(hex, self._data)) + '))'
    
    def __int__(self):
        '''
        Converts the data to an int if it contains exactly one byte.
        '''
        if self.__len__() != 1:
            raise TypeError('must be of length 1')
        return self._data[0]
    
    def index(self, byte):
        '''
        Returns index of byte in RawData.
        Raises ValueError if byte is not in RawData and TypeError if can't be
        converted RawData or its length is not 1.
        '''
        if not isinstance(byte, RawData):
            try:
                byte = self.__class__(byte)
            except (TypeError, ValueError):
                raise TypeError("can't convert byte to RawData")
        if len(byte) != 1:
            raise TypeError('byte must be of length 1')
        try:
            return self._data.index(byte._data[0])
        except ValueError:
            raise ValueError('byte not in RawData')

    def split(self, byte, maxsplit=-1):
        '''
        Splits RawData on every occurrence of byte.
        '''
        if (maxsplit == 0):
            return [self]
        try:
            ind = self.index(byte)
        except ValueError:
            return [self]
        return [self.__class__(self._data[:ind])] + self.__class__(self._data[ind+1:]).split(byte, maxsplit-1)

    def toString(self):
        return String(self.export().decode('utf-8'))
    
    def export(self):
        '''
        Returns the data as bytes() so that you can use it for methods that
        expect bytes. Don't use this for comparison!
        '''
        if bytes == str:
            return bytes().join(map(chr,self._data))
        return bytes(self._data)


    bytes = newbytes
