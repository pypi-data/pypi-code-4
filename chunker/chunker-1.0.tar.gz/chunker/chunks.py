import __future__

import copy
import os


class Chunk(object):
    """
    Chunk in the file. A chunk usually contains a signature indicating its
    type, and a group of data fields.

    :param fp: File object to read from.
    :param parser: The parser it belongs to. It's optional and you can leave it None.

    To define your chunk class, you should follow these steps:

    1. Define its fields. Fields are populated in this order. See :doc:`fields` for more information.

    2. Define a static :meth:`matches` method to judge if the following bytes match this type of chunk.

    Example::

        import os
        import struct

        class DataChunk:
            Fields = (
                UnsignedLongField('type'),
                UnsignedLongField('data_length'),
                StringField('data', length_field_name='data_length'),
            )

            @staticmethod
            def matches(fp):
                buf = fp.read(4)
                type = struct.unpack('>H', buf)[0]

                # IMPORTANT! Reset position if you need to populate this type
                # field or type doesn't match
                fp.seek(-4, os.SEEK_CUR)

                return type == 0x01020304

        if DataChunk.matches(fp):
            c = DataChunk(fp, None)
            print(c.data) # Access field value by its name
    """
    Fields = ()

    def __new__(cls, *args, **kargs):
        instance = super(Chunk, cls).__new__(cls)
        instance.fields = copy.deepcopy(cls.Fields)
        instance.fields_map = {f.name: f for f in instance.fields}
        return instance

    def __init__(self, fp, parser):
        self.fp = fp
        self.parser = parser

    def __getattr__(self, key):
        return self.fields_map[key].value

    @staticmethod
    def matches(fp):
        """
        Read next a few bytes to judge if the following data match this type
        of chunk.

        You should override this method or it will return :const:`False` by default.

        :param fp: File object to read from.
        :returns: If the following bytes match this chunk type.
        """
        return False

    def populate(self):
        """
        Populate chunk fields. After that, you can access each field data
        directly by field name.
        """
        for field in self.fields:
            field.populate(self.fp, self)
            # if self.parser is not None and self.parser.is_debug:
            #     print('%s: %s @ %s' % (
            #         field.name, field.value, hex(self.fp.tell())))

    def __str__(self):
        dumps = []
        dumps.append('----------')
        dumps.append(self.__class__.__name__)
        dumps.append('----------')
        for field in self.fields:
            dumps.append('%s: %s' % (field.name, field.value))
        dumps.append('==========')
        return '\n'.join(dumps)
