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
WordPress service recognizes the following options in :ref:`brc.py`:

.. code:: python

  service = 'wordpress'
  service_options = {
    'blog': <blog url>,
    'username': 'user01',
    'password': 'secret',
  }

``blog`` should be the URL of WordPress blog, for example,
``http://<something>.wordpress.com/`` or ``http://example.com/wordpress/``.
Note that the tailing slash must be included.

In order to use WordPress XML-RPC API, you must provide ``username`` and
``password``.
"""

from __future__ import print_function
import sys

from wordpress_xmlrpc import Client, WordPressPage, WordPressPost
from wordpress_xmlrpc.methods import posts

from bpy.services.base import Service as BaseService
from bpy.handlers import find_handler


class Service(BaseService):

  service_name = 'wordpress'

  def __init__(self, *args, **kwargs):

    super(Service, self).__init__(*args, **kwargs)

    self.service = None

  def auth(self):

    self.service = Client(self.options['blog'] + 'xmlrpc.php',
                          self.options['username'],
                          self.options['password'])

  def make_handler_post(self):

    handler = find_handler(self.filename)
    if not handler:
      print('No handler for the file!')
      sys.exit(1)

    hdr = handler.header

    post = {
      'service': self.service_name,
      'kind': hdr.get('kind', 'post'),
      'content': handler.generate(),
    }
    if isinstance(self.options['blog'], type('')):
      post['blog'] = {'id': self.options['blog']}
    post.update(handler.generate_post())

    return handler, post

  def post(self):

    handler, post = self.make_handler_post()

    if 'blog' not in post:
      print('You need to specify which blog to post on '
            'in either brc.py or header of %s.' % handler.filename)
      sys.exit(1)

    self.auth()

    kind = post['kind']
    title = post['title']

    if kind == 'post':
      wpost = WordPressPost()
    else:
      wpost = WordPressPage()

    wpost.title = title
    wpost.content = post['content']
    wpost.post_status = 'draft' if post['draft'] else 'publish'
    wpost.terms_names = {
      'post_tag': post['labels'],
      'category': post['categories'] if 'categories' in post else [],
    }

    resp = {}
    if 'id' in post:
      print('Updating a %s: %s' % (kind, title))
      self.service.call(posts.EditPost(post['id'], wpost))
    else:
      print('Posting a new %s: %s' % (kind, title))
      wpost.id = self.service.call(posts.NewPost(wpost))
      wpost = self.service.call(posts.GetPost(wpost.id))
      resp['id'] = wpost.id
      resp['url'] = wpost.link

    for k in ('service', 'blog', 'kind', 'draft'):
      resp[k] = post[k]

    handler.merge_header(resp)
    handler.write()
