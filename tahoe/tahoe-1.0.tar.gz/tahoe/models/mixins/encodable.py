"""
The MIT License (MIT)

Copyright (c) 2013 Lunar Technology Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""


class EncoderMixin(object):
    """
    Provides a method for encoding a model-defined encoder and decoder chain.
    Allows you to take some kind of data, say a Python object, and serialize
    it to some form, say for storing in a database.

    Imagine if you want to encode an object into a format that can be stored
    in a database text field and be reconstitutable into a python object
    again in the future.

    You might define an encoder-decoder chain like so:

    .. code-block:: python

        encode_decode_chain = [
            (pickle.dumps, pickle.loads),
            (base64.b64encode, base64.b64decode)
            ]

    This implies that when encoding data passed into the `cls.encode`
    method, the data would first be run through `pickle.dumps` and then
    ``base64.b64encode``.

    When decoding it would work the other way around, running the encoded
    data first through ``base64.b64decode`` and then ``pickle.loads``.

    Pickle could be replaced with JSON, and the text encoding could be replaced
    with gzip encoding, for example.
    """
    encode_decode_chain = []

    @classmethod
    def encode(cls, data):
        for link in cls.encode_decode_chain:
            data = link[0](data)
        return data

    @classmethod
    def decode(cls, data):
        for link in reversed(cls.encode_decode_chain):
            data = link[1](data)
        return data
