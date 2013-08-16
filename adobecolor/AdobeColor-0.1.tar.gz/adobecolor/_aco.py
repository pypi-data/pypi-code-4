import struct

from _color import Color
import _helper

class _ColorReader(object):
    def __init__(self, stream, offset, count):
        self._stream = stream
        self._offset = offset
        self._count = count

    def __iter__(self):
        for i in range(self._count):
            self._offset, color_space = _helper.get_ushort(self._stream, self._offset)
            self._offset, w = _helper.get_ushort(self._stream, self._offset)
            self._offset, x = _helper.get_ushort(self._stream, self._offset)
            self._offset, y = _helper.get_ushort(self._stream, self._offset)
            self._offset, z = _helper.get_ushort(self._stream, self._offset)
            yield "Unnamed Color {0}".format(i+1), Color.from_adobe(color_space, w, x, y, z)

class _ColorReaderWithName(_ColorReader):
    def _read_name(self):
        """ Word size = 2 """

        # Marks the start of the string
        self._offset, _ = _helper.validate_ushort_is_any(self._stream, (0, ), self._offset)
        self._offset, length = _helper.get_ushort(self._stream, self._offset)
        
        data = self._stream[self._offset:self._offset+(length-1)*2]

        name = data.decode('utf-16-be')
        self._offset += (length-1)*2
  
        self._offset, _ = _helper.validate_ushort_is_any(self._stream, (0, ), self._offset)
        return name


    def __iter__(self):
        colors = tuple(super(_ColorReaderWithName, self).__iter__())  # Version 1 information can be ignored
        self._offset, _ = _helper.validate_ushort_is_any(self._stream, (2, ), self._offset)
        self._offset, length = _helper.get_ushort(self._stream, self._offset)
        if length != len(colors):
            raise ValueError("Length of names is not the same as the length of colors")

        for name, color in super(_ColorReaderWithName, self).__iter__():
            name = self._read_name()
            yield name, color

class Aco(object):
    READERS = [ _ColorReader, _ColorReaderWithName ]
    def __init__(self, stream):
	offset, self._version = _helper.validate_ushort_is_any(stream, (0, 1))
        offset, self._color_count = _helper.get_ushort(stream, offset)

        self._colors = [ 
        ]
        self._key_mapping = {
        }

        self._read_colors(stream, offset)

    def _read_colors(self, stream, offset):
        reader = self.READERS[self._version](stream, offset, self._color_count)
        index = 0
        for name, color in reader:
            self._colors.append(color)
            self._key_mapping[name] = index
            index += 1
        

    def keys(self):
        return self._key_mapping.keys()

    @property
    def length(self):
        return self._color_count

    def __getitem__(self, value):
        # if we are not a number, assume a key, and look it up
        if not isinstance(value, (int, long)):
            value = self._key_mapping[value]

        return self._colors[value]
