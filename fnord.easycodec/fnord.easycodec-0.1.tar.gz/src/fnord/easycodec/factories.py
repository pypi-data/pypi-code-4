# -*- coding: utf-8 -*-

# Copyright 2013, Bert Vanderbauwhede
#
# This file is part of fnord.easycodec.
#
# fnord.easycodec is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# fnord.easycodec is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with fnord.easycodec.  If not, see <http://www.gnu.org/licenses/>.

import codecs
import sys

AUTO = object()


def CodecRegistration(name, encode, decode,
                      incrementalencoder=None, incrementaldecoder=None,
                      streamreader=None, streamwriter=None):
    """Factory for a codec-registration.
    """

    class MyCodec(codecs.Codec):

        def encode(self, string, errors="strict"):
            return encode(string, errors=errors)

        def decode(self, string, errors="strict"):
            return decode(string, errors=errors)

    if streamreader is AUTO:
        class MyStreamReader(MyCodec, codecs.StreamReader):
            pass

        streamreader = MyStreamReader

    if streamwriter is AUTO:
        class MyStreamWriter(MyCodec, codecs.StreamWriter):
            pass

        streamwriter = MyStreamWriter

    if sys.version >= "2.5":
        if incrementalencoder is AUTO:
            class MyIncrementalEncoder(codecs.IncrementalEncoder):

                def __init__(self, errors="strict"):
                    if errors != "strict":
                        raise UnicodeError(
                            u"Unsupported error handling: %s" % errors)

                    super(MyIncrementalEncoder, self).__init__(errors)

                def encode(self, string, final=False):
                    self.buffer += string

                    if final:
                        return encode(self.buffer, errors=self.errors)
                    else:
                        return ""

            incrementalencoder = MyIncrementalEncoder

        if incrementaldecoder is AUTO:
            class MyIncrementalDecoder(codecs.IncrementalDecoder):

                def __init__(self, errors="strict"):
                    if errors != "strict":
                        raise UnicodeError(
                            u"Unsupported error handling: %s" % errors)

                    super(MyIncrementalDecoder, self).__init__(errors)

                def decode(self, string, final=False):
                    self.buffer += string

                    if final:
                        return decode(self.buffer, errors=self.errors)
                    else:
                        return ""

            incrementaldecoder = MyIncrementalDecoder

        return codecs.CodecInfo(
            name=name,
            encode=encode,
            decode=decode,
            incrementalencoder=incrementalencoder,
            incrementaldecoder=incrementaldecoder,
            streamreader=streamreader,
            streamwriter=streamwriter)

    else:
        return (encode, decode, streamreader, streamwriter)


def CodecSearch(name, encode, decode,
                incrementalencoder=None, incrementaldecoder=None,
                streamreader=None, streamwriter=None):
    """Factory for a codec-search.
    """
    def my_search(encoding):
        if encoding == name:
            return CodecRegistration(
                name=name,
                encode=encode,
                decode=decode,
                incrementalencoder=incrementalencoder,
                incrementaldecoder=incrementaldecoder,
                streamreader=streamreader,
                streamwriter=streamwriter)
        else:
            return None

    return my_search
