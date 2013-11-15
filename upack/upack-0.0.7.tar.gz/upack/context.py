# Copyright (c) 2013, Robert Escriva
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of upack nor the names of its contributors may be used
#       to endorse or promote products derived from this software without
#       specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import with_statement


import shutil
import string

from upack import Package, SubPackage


__all__ = ('Context',)


class Raw(object):

    def __init__(self, x):
        self.x = x


class Context(object):

    def __init__(self):
        self.ctx = []
        self.to_clean = []

    def push(self, d):
        if isinstance(d, Package) or isinstance(d, SubPackage):
            package = d
            d = {}
            d['build-requires'] = ''
            d['requires'] = ''
            d['conflicts'] = ''
            d['name'] = package.name
            d['description'] = package.description
            d.update(package.options)
            self.ctx.append(d)
        else:
            self.ctx.append(d)

    def pop(self):
        self.ctx.pop()

    def clean(self):
        for x in self.to_clean:
            shutil.rmtree(x)

    def cleanup(self, dirname):
        self.to_clean.append(dirname)

    def get_from_ctx(self, s):
        for d in reversed(self.ctx):
            if s in d:
                return d[s]
        return None

    def format(self, s):
        return self._format(s)

    def _format(self, s, history=()):
        keys = [x[1] for x in string.Formatter().parse(s) if x[1]]
        d = {}
        for k in keys:
            if k in history:
                raise RuntimeError('cycle %s->%s' % ('->'.join(history), k))
            x = self.get_from_ctx(k)
            if x is None:
                raise KeyError('missing value for "%s"' % k)
            if isinstance(x, Raw):
                d[k] = x.x
            else:
                d[k] = self._format(x, history + (k,))
        return s.format(**d)
