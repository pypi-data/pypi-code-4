#!/usr/bin/python
from . import tags, ids

import unittest, os
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

class TestEncodeAndDecode(unittest.TestCase):
    def setUp(self):
        if 'PYNBTTESTPATH' in os.environ:
            self.output = open(os.environ['PYNBTTESTPATH'], "wb+")
        else:
            self.output = StringIO.StringIO()
        self.maxDiff = None
    def test_roundtrip(self):
        self.data = tags.CompoundTag({
            u"byte" : tags.ByteTag(4),
            u"short" : tags.ShortTag(0x7FFF),
            u"int" : tags.IntTag(12345),
            u"long" : tags.LongTag(1L),
            # Leave out float and double to avoid floating-point errors
            u"unicode" : tags.StringTag(u"Here's an acc\u00c9nt!"),
            u"list" : tags.ListTag([
                tags.CompoundTag({
                    u"name": tags.StringTag(u"foo"),
                    u"value": tags.IntTag(12),
                }),
                tags.CompoundTag({
                    u"name": tags.StringTag(u"bar"),
                    u"value": tags.IntTag(21),
                }),
            ], ids.TAG_Compound),
            u"bytearray" : tags.ByteArrayTag("Hello world!"),
            u"intlist" : tags.IntArrayTag([1,2,3]),
        })
        self.do_roundtrip()
        self.assertEqual(self.lvalues, self.rvalues)
    def test_pathological(self):
        self.data = tags.CompoundTag({
            u"list" : tags.ListTag([tags.EndTag(), tags.EndTag(), 
                                    tags.EndTag()], ids.TAG_End),
        })
        self.do_roundtrip()
        self.assertEqual(self.lvalues, self.rvalues)
    def do_roundtrip(self):
        enclen = self.data.encode_named(u"", self.output)
        self.output.seek(0)
        decname, decoded = tags.decode_named(self.output)
        self.lvalues = (u'', self.data)
        self.rvalues = (decname, decoded)
    def tearDown(self):
        self.output.close()
