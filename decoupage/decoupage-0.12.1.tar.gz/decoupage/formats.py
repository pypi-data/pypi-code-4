"""
pluggable formats for directory listings
"""

import datetime
import PyRSS2Gen
from utils import link
try:
  import json as json
except ImportError:
  import simplejson as json

class JSON(object):
  """
  JSON format for index pages
  just (basically) return the data
  """

  def __init__(self, app):
    self.app = app

  def __call__(self, request, data):

    # fix datetime
    for f in data['files']:
      if 'modified' in f:
        f['modified'] = f['modified'].ctime()

    return 'application/json', json.dumps(data['files'])

class RSS(object):
  """RSS for indices"""

  def __init__(self, app, count=10, cascade=False):
    self.app = app # the decoupage
    self.count = int(count)
    self.cascade = cascade

  def __call__(self, request, data):
    items = [ PyRSS2Gen.RSSItem(title=item['name'],
                                description=item['description'] or item.get('title') or item['name'],
                                pubDate=item['modified'],
                                guid=PyRSS2Gen.Guid(link(request, item['path'])))
              for item in data['files'] ]
    path_link = link(request, data['path'])
    description = data.get('title') or data['path']
    rss = PyRSS2Gen.RSS2(title=description,
                         link=path_link,
                         description=description,
                         lastBuildDate = datetime.datetime.now(),
                         items=items
                         )
    return 'application/rss+xml', rss.to_xml()
