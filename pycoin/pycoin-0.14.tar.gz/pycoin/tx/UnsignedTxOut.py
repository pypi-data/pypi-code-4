# -*- coding: utf-8 -*-
"""
A template for unsigned transactions.

The MIT License (MIT)

Copyright (c) 2013 by Richard Kiss

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

from ..serialize.bitcoin_streamer import stream_struct

class UnsignedTxOut(object):
    def __init__(self, previous_hash, previous_index, coin_value, script, sequence=4294967295):
        self.previous_hash = previous_hash
        self.previous_index = previous_index
        self.coin_value = coin_value
        self.script = script
        self.sequence = sequence

    def clone(self):
        return self.__class__(self.previous_hash, self.previous_index, self.coin_value, self.script)

    def stream(self, f):
        stream_struct("#LSL", f, self.previous_hash, self.previous_index, self.script, self.sequence)
