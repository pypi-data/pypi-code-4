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


services = {
  'Base': {
    'match': re.compile(r'^base$', re.I),
    'module': 'bpy.services.base',
  },
  'Blogger': {
    'match': re.compile(r'^(b|blogger)$', re.I),
    'module': 'bpy.services.blogger',
  },
  'WordPress': {
    'match': re.compile(r'^(wp|wordpress)$', re.I),
    'module': 'bpy.services.wordpress',
  },
}


def find_service(service_name, service_options, *args, **kwargs):

  sys.path.insert(0, os.getcwd())
  module = None
  for name, hdlr in services.items():
    if hdlr['match'].match(service_name):
      try:
        module = __import__(hdlr['module'], fromlist=['Service'])
        break
      except Exception:
        print('Cannot load module %s of service %s' % (hdlr['module'], name))
        traceback.print_exc()
  sys.path.pop(0)
  if module:
    return module.Service(service_options, *args, **kwargs)
  return None
