# -*- coding: utf-8 -*-

import os
import shutil
import zipfile

from tempfile import mktemp
from lxml import etree
from json import loads


class GoogleReaderTakeout(object):

    def __init__(self, file_obj):
        self.directory = ""
        self.temp = mktemp()
        self._unpack(file_obj)

    def _unpack(self, file_obj):
        z = zipfile.ZipFile(file_obj)
        z.extractall(path=self.temp)
        for (path, dirs, files) in os.walk(self.temp):
            if 'subscriptions.xml' in files:
                self.directory = path
        z.close()

    def _load_xml_file(self, filename):
        subscriptions = '%s/%s.xml' % (self.directory, filename)
        return etree.XML(''.join(open(subscriptions).readlines()))

    def _load_json_file(self, filename):
        json_file = '%s/%s.json' % (self.directory, filename)
        return loads(''.join(open(json_file).readlines()))

    def subscriptions(self):
        grab = self._load_xml_file('subscriptions')
        data = []
        for element in grab.xpath('//opml/body/outline'):
            if element.get('type') is None:
                # if type is none it's a category
                for child in element.getchildren():
                    data.append({
                        'text': child.get('text'),
                        'title': child.get('title'),
                        'type': child.get('type'),
                        'xmlUrl': child.get('xmlUrl'),
                        'htmlUrl': child.get('htmlUrl'),
                        'category': element.get('title'),
                    })
            else:
                data.append({
                    'text': element.get('text'),
                    'title': element.get('title'),
                    'type': element.get('type'),
                    'xmlUrl': element.get('xmlUrl'),
                    'htmlUrl': element.get('htmlUrl'),
                    'category': None,
                })
        return data

    def __getattr__(self):
        def method(*args, **kwargs):
            getattr(self, '_load_json_file')(*args, **kwargs)
        return method

    def __del__(self):
        shutil.rmtree(self.temp)
