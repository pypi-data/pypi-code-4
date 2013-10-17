#!/usr/bin/env python
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
============
b.py command
============


Commands
========

============= =======================
command       supported services
============= =======================
``blogs``     ``b``
``post``      ``b``, ``wp``
``generate``  ``base``, ``b``, ``wp``
``checklink`` ``base``, ``b``, ``wp``
``search``    ``b``
============= =======================

Descriptions:

``blogs``
  list blogs. This can be used for blog IDs lookup.

``post``
   post or update a blog post.

``generate``
  generate HTML file at ``<TEMP>/draft.html``, where ``<TEMP>`` is the system's
  temporary directory.

  The generation can output a preview html at ``<TEMP>/preview.html`` if there
  is ``tmpl.html``. It will replace ``%%Title%%`` with post title and
  ``%%Content%%`` with generated HTML.

``checklink``
  check links in generated HTML using lnkckr_.

``search``
  search blog

.. _lnkckr: https://pypi.python.org/pypi/lnkckr
"""

from __future__ import print_function
import argparse as ap
import imp
import os
import sys
import traceback

from bpy.handlers import handlers
from bpy.services import services, find_service

__program__ = 'b.py'
__description__ = 'Post to Blogger or WordPress in markup language seamlessly'
__copyright__ = 'Copyright 2013, Yu Jie Lin'
__license__ = 'MIT License'
__version__ = '0.7.0'
__website__ = 'http://bitbucket.org/livibetter/b.py'

__author__ = 'Yu-Jie Lin'
__author_email__ = 'livibetter@gmail.com'


# b.py stuff
############

# filename of local configuration without '.py' suffix.
BRC = 'brc'


def parse_args():

  p = ap.ArgumentParser()
  p.add_argument('--version', action='version',
                 version='%(prog)s ' + __version__)
  p.add_argument('-s', '--service', default='base',
                 help='what service to use. (Default: %(default)s)')
  sp = p.add_subparsers(help='commands')

  pblogs = sp.add_parser('blogs', help='list blogs')
  pblogs.set_defaults(subparser=pblogs, command='blogs')

  psearch = sp.add_parser('search', help='search for posts')
  psearch.add_argument('-b', '--blog', help='Blog ID')
  psearch.add_argument('q', nargs='+', help='query text')
  psearch.set_defaults(subparser=psearch, command='search')

  pgen = sp.add_parser('generate', help='generate html')
  pgen.add_argument('filename')
  pgen.set_defaults(subparser=pgen, command='generate')

  pchk = sp.add_parser('checklink', help='check links in chkerateed html')
  pchk.add_argument('filename')
  pchk.set_defaults(subparser=pchk, command='checklink')

  ppost = sp.add_parser('post', help='post or update a blog post')
  ppost.add_argument('filename')
  ppost.set_defaults(subparser=ppost, command='post')

  args = p.parse_args()
  return args


def load_config():

  rc = None
  try:
    search_path = [os.getcwd()]
    _mod_data = imp.find_module(BRC, search_path)
    print('Loading local configuration...')
    try:
      rc = imp.load_module(BRC, *_mod_data)
    finally:
      if _mod_data[0]:
        _mod_data[0].close()
  except ImportError:
    pass
  except Exception:
    traceback.print_exc()
    print('Error in %s, aborted.' % _mod_data[1])
    sys.exit(1)
  return rc


def main():

  args = parse_args()

  rc = load_config()
  service_options = {'blog': None}
  if rc:
    if hasattr(rc, 'handlers'):
      for name, handler in rc.handlers.items():
        if name in handlers:
          handlers[name].update(handler)
        else:
          handlers[name] = handler.copy()
    if hasattr(rc, 'services'):
      for name, service in rc.services.items():
        if name in services:
          services[name].update(service)
        else:
          services[name] = service.copy()
    if hasattr(rc, 'service'):
      args.service = rc.service
    if hasattr(rc, 'service_options'):
      service_options.update(rc.service_options)

  if hasattr(args, 'blog') and args.blog is not None:
    service_options['blog'] = args.blog
  filename = args.filename if hasattr(args, 'filename') else None
  service = find_service(args.service, service_options, filename)

  if args.command == 'blogs':
    service.list_blogs()
  elif args.command == 'search':
    service.search(' '.join(args.q))
  elif args.command == 'generate':
    service.generate()
  elif args.command == 'checklink':
    service.checklink()
  elif args.command == 'post':
    service.post()


if __name__ == '__main__':
  main()
