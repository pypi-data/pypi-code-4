#!/usr/bin/env python
"""
Copyright (C) 2013 Legoktm

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
IN THE SOFTWARE.
"""

import os
import json


class JSON:
    def __init__(self, filename=None):
        if not filename:
            self.filename = 'cache.json'
        else:
            self.filename = filename
        if not self.filename.endswith('.json'):
            self.filename += '.json'
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                self.d = json.load(f)
        else:
            self.d = {}

    def save(self):
        with open(self.filename, 'w') as f:
            json.dump(self.d, f)

    def set(self, key, value, *args):
        self.d[key] = value
        self.save()

    def get(self, key):
        return self.d[key]

    def delete(self, key):
        del self.d[key]
        self.save()

    def __contains__(self, key):
        return key in self.d
