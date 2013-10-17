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

"""
Markup handlers' IDs and extensions:

==================== ========================================================
ID                   extensions
==================== ========================================================
``AsciiDoc``         ``.asciidoc``
``HTML``             ``.html``, ``.htm``, ``.raw``
``Markdown``         ``.md``, ``.mkd``, ``.mkdn``, ``.mkdown``, ``.markdown``
``reStructuredText`` ``.rst``
``Text``             ``.txt``, ``.text``
==================== ========================================================


Options
=======

The general options are supported by all handlers, defined in
:class:`bpy.handlers.base.BaseHandler`, but they have to be specified per
handler basis, the following sample code shows the options and their default
value:

.. code:: python

  handlers = {
    '<MARKUP HANDLER ID>': {
      'options': {
        # prefix string to HTML ID to avoid conflict
        'id_affix': None,

        # string to prepend to actual markup
        'markup_prefix': '',

        # string to append to actual markup
        'markup_suffix': '',

        # use smartypant to process the output of markup processor
        'smartypants': False,
      },
    },
  }

.. _id_affix:

``id_affix``
------------

``id_affix`` is used to avoid conflict across posts' HTML element ID. It may be
a prefix or suffix, depending on handler's implementation and markup library's
support. It has three types of value:

1. ``None``: no affix to ID.
2. non-empty string: the string is the affix.
3. empty string: the affix is generated automatically.

Currently supported markup handler:

* :mod:`bpy.handlers.rst`

``markup_prefix`` and ``markup_suffix``
---------------------------------------

``markup_prefix`` and ``markup_suffix`` can be useful for adding header and
footer content for posts. Another useful case in reStructuredText is you can
use it for setting up some directives, for example ``.. sectnum::``, so you can
ensure all posts have prefixing section number if in use conjunction with
``.. contents::``.

``smartypants``
---------------

If ``smartypants`` is enabled, then all generated HTML from markup processor
will be processed by smartypants_ library.

.. _smartypants: https://pypi.python.org/pypi/smartypants


.. _custom-handler:

Writing a custom handler
========================

A sample handler ``sample_handler.py``:

.. code:: python

  from bpy.handlers import base

  class Handler(base.BaseHandler):
    PREFIX_HEAD = ''
    PREFIX_END = ''
    HEADER_FMT = '%s: %s'

    def _generate(self, markup=None):
      if markup is None:
        markup = self.markup

      html = do_process(markup)
      return html

And corresponding setting in ``brc.py``:

.. code:: python

  import re

  handlers = {
    'SampleHandler': {
      'match': re.compile(r'.*\.ext$'),
      'module': 'sample_handler',
    },
  }
"""

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
