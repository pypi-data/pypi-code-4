# Copyright (C) 2013 by Yu-Jie Lin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import os
import re
import sys
import traceback


handlers = {
  'AsciiDoc': {
    'match': re.compile(r'.*\.asciidoc$'),
    'module': 'bpy.handlers.asciidoc',
  },
  'HTML': {
    'match': re.compile(r'.*\.(html?|raw)$'),
    'module': 'bpy.handlers.html',
  },
  'Markdown': {
    'match': re.compile(r'.*\.(markdown|md(own)?|mkdn?)$'),
    'module': 'bpy.handlers.mkd',
  },
  'reStructuredText': {
    'match': re.compile(r'.*\.rst$'),
    'module': 'bpy.handlers.rst',
  },
  'Text': {
    'match': re.compile(r'.*\.te?xt$'),
    'module': 'bpy.handlers.text',
  },
}


def find_handler(filename):

  sys.path.insert(0, os.getcwd())
  module = None
  for name, hdlr in handlers.items():
    if hdlr['match'].match(filename):
      try:
        module = __import__(hdlr['module'], fromlist=['Handler'])
        break
      except Exception:
        print('Cannot load module %s of handler %s' % (hdlr['module'], name))
        traceback.print_exc()
  sys.path.pop(0)
  if module:
    return module.Handler(filename, hdlr.get('options', {}))
  return None
